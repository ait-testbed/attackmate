import logging
import json
from typing import Dict, Any, Optional

from attackmate.executors.executor_factory import executor_factory
from attackmate_client import RemoteAttackMateClient
from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.schemas.config import RemoteConfig
from attackmate.schemas.remote import AttackMateRemoteCommand
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.processmanager import ProcessManager
from attackmate.variablestore import VariableStore

output_logger = logging.getLogger('output')


@executor_factory.register_executor('remote')
class RemoteExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, varstore: VariableStore, cmdconfig=None, *,
                 remote_config: Dict[str, RemoteConfig] = {}):
        super().__init__(pm, varstore, cmdconfig)
        self.logger = logging.getLogger('playbook')
        self.remote_config = remote_config
        # client_cache
        self._clients_cache: Dict[str, RemoteAttackMateClient] = {}

    def _get_connection_info(self, command: AttackMateRemoteCommand) -> Dict[str, Any]:
        """
        Helper to resolve configuration details without instantiating a client.

        Returns:
            Dictionary containing connection information (name, url, user, pass, cafile)
        """
        if command.connection:
            conn_name = command.connection
        elif self.remote_config:
            # Use first connection in config if none specified
            conn_name = next(iter(self.remote_config))
            self.logger.debug(f'No connection specified, using default: {conn_name}')
        else:
            raise ExecException('No remote connections configured in AttackMate config.')

        if conn_name not in self.remote_config:
            raise ExecException(f"Remote connection '{conn_name}' not found in config.")

        config = self.remote_config[conn_name]
        self.logger.debug(
            f"Resolved connection '{conn_name}' with URL: {config.url}, "
            f'User: {config.username}, CA Cert: {config.cafile}')
        return {
            'name': conn_name,
            'url': self.varstore.substitute(config.url),
            'user': self.varstore.substitute(config.username) if config.username else None,
            'pass': self.varstore.substitute(config.password) if config.password else None,
            'cafile': self.varstore.substitute(config.cafile) if config.cafile else None
        }

    def setup_connection(self, command: AttackMateRemoteCommand) -> RemoteAttackMateClient:
        """
        Resolves info and returns a cached or new client.

        Args:
            command: The remote command containing connection information

        Returns:
            RemoteAttackMateClient instance (cached or newly created)
        """
        info = self._get_connection_info(command)
        conn_name = info['name']

        if conn_name in self._clients_cache:
            self.logger.debug(f'Using cached remote client for: {conn_name}')
            return self._clients_cache[conn_name]

        self.logger.debug(f'Creating new remote client for: {conn_name} ({info["url"]})')
        self.logger.debug(
            f'Attempting to connect to remote AttackMate server at {info["url"]} '
            f'with user {info["user"]}, certificate={info["cafile"]}')
        try:
            client = RemoteAttackMateClient(
                server_url=info['url'],
                username=info['user'],
                password=info['pass'],
                cacert=info['cafile']
            )
            self._clients_cache[conn_name] = client
            self.logger.info(f'Successfully created remote client for: {conn_name}')
            return client

        except Exception as e:
            self.logger.error(f'Failed to create remote client for {conn_name}: {e}', exc_info=True)
            raise ExecException(f'Failed to create remote client for {conn_name}: {e}')

    def log_command(self, command: AttackMateRemoteCommand) -> None:
        try:
            # Resolve the URL and Name for the log without creating a client
            info = self._get_connection_info(command)
            target_str = f"{info['name']} ({info['url']})"
        except Exception:
            target_str = command.connection or 'unknown connection'

        self.logger.info(
            f"Executing REMOTE AttackMate command: Type='{command.type}', "
            f"RemoteCmd='{command.cmd}' on server {target_str}"
        )

        remote_command_json = (
            command.remote_command.model_dump() if command.remote_command else ' '
        )
        output_logger.info(
            f"Remote Command '{remote_command_json}' sent to {target_str}"
        )

    async def _exec_cmd(self, command: AttackMateRemoteCommand) -> Result:
        try:
            client = self.setup_connection(command)
            response_data = self._dispatch_remote_command(client, command)
            success, error_msg, stdout, return_code = self._process_response(response_data)

        except (ExecException, IOError, FileNotFoundError) as e:
            self.logger.error(f'Execution failed: {e}', exc_info=True)
            success, error_msg, stdout, return_code = False, str(e), None, 1

        except Exception as e:
            error_message = f'Remote executor encountered an unexpected error: {e}'
            self.logger.error(error_message, exc_info=True)
            success, error_msg, stdout, return_code = False, error_message, None, 1

        final_stdout = self._format_output(success, stdout, error_msg)
        final_return_code = return_code if return_code is not None else (0 if success else 1)

        return Result(final_stdout, final_return_code)

    def _dispatch_remote_command(
        self, client: RemoteAttackMateClient, command: AttackMateRemoteCommand
    ) -> Dict[str, Any]:
        """
        Dispatches the command to the appropriate client method.

        Args:
            client: The RemoteAttackMateClient instance
            command: The remote command to dispatch

        Returns:
            Response dictionary from the remote server
        """
        debug = getattr(command, 'debug', False)
        self.logger.debug(f"Dispatching command '{command.cmd}' with debug={debug}")

        if command.cmd == 'execute_playbook' and command.playbook_yaml_path:
            try:
                with open(command.playbook_yaml_path, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
                response = client.execute_remote_playbook_yaml(yaml_content, debug=debug)
            except FileNotFoundError as e:
                raise ExecException(f'Playbook file not found: {command.playbook_yaml_path}') from e
            except IOError as e:
                raise ExecException(f'Failed to read playbook file {command.playbook_yaml_path}: {e}') from e

        elif command.cmd == 'execute_command':
            response = client.execute_remote_command(command.remote_command, debug=debug)

        else:
            raise ExecException(f"Unsupported remote command: '{command.cmd}'")

        return response if response is not None else {}

    def _process_response(self,
                          response_data: Optional[Dict[str,
                                                       Any]]) -> tuple[bool,
                                                                       Optional[str],
                                                                       Optional[str],
                                                                       int]:
        """
        Processes the raw response from the remote client to determine success,
        error message, return code, and stdout string.

        Args:
            response_data: The response dictionary from the remote server

        Returns:
            Tuple of (success, error_message, stdout_str, return_code)
        """
        success: bool = False
        error_message: Optional[str] = None
        stdout_str: Optional[str] = None
        return_code: int = 1

        if not response_data:
            error_message = 'No response received from remote server (client communication failed).'
            self.logger.error(error_message)
            return success, error_message, stdout_str, return_code

        self.logger.debug(f'Processing response data: {json.dumps(response_data)}')

        # Prioritize 'result' key for command-like responses
        cmd_result = response_data.get('result', {})
        if cmd_result:
            success = cmd_result.get('success', False)
            stdout_str = cmd_result.get('stdout')
            return_code = cmd_result.get('returncode', 1 if not success else 0)
            if not success and 'error_message' in cmd_result:
                error_message = cmd_result['error_message']
                self.logger.error(f'Remote command reported error: {error_message}')
            else:
                self.logger.info(f'Remote command execution success: {success}, return code: {return_code}')

        # Fallback to 'success' key for playbook-like responses
        elif 'success' in response_data:
            success = response_data.get('success', False)
            stdout_str = json.dumps(response_data, indent=2)
            return_code = 0 if success else 1
            if not success:
                error_message = response_data.get('message', 'Unknown error during playbook execution.')
                self.logger.error(f'Remote playbook execution failed: {error_message}')
            else:
                self.logger.info(f'Remote playbook execution success: {success}')

        # Catch all for unexpected response structures
        else:
            error_message = 'Received unexpected response structure from remote server.'
            stdout_str = json.dumps(response_data, indent=2)
            self.logger.warning(f'{error_message}: {stdout_str}')

        return success, error_message, stdout_str, return_code

    def _format_output(self, success: bool, stdout: Optional[str], error: Optional[str]) -> str:
        """
        Creates the final stdout string based on the execution result.

        Args:
            success: Whether the operation was successful
            stdout: Standard output from the operation
            error: Error message if any

        Returns:
            Formatted output string
        """
        if error:
            # Prepend the error to the standard output if both exist
            header = f'Error: {error}'
            return f'{header}\n\nOutput/Response:\n{stdout}' if stdout else header

        if stdout is not None:
            return stdout

        return 'Operation completed successfully.' if success else 'Operation failed with no output.'

    def cleanup(self) -> None:
        """
        Cleans up all cached remote clients by closing connections and clearing the cache.
        Should be called when the executor is being destroyed or reset.
        """
        if not self._clients_cache:
            return

        self.logger.debug(f'Cleaning up {len(self._clients_cache)} remote client(s)')

        for conn_name, client in self._clients_cache.items():
            try:
                self.logger.debug(f'Closing remote client connection: {conn_name}')
                # Attempt to close the client connection if it has a close method
                if hasattr(client, 'close'):
                    client.close()
                elif hasattr(client, 'disconnect'):
                    client.disconnect()
                self.logger.info(f'Remote client {conn_name} closed successfully.')
            except Exception as e:
                self.logger.error(f'Failed to close remote client {conn_name}: {str(e)}')

        # Clear the cache
        self._clients_cache.clear()
        self.logger.debug('Remote client cache cleared.')
