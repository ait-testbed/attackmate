import logging
import json
from typing import Dict, Any, Optional

from attackmate.executors.executor_factory import executor_factory
from attackmate_client import RemoteAttackMateClient
from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.schemas.remote import AttackMateRemoteCommand
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.processmanager import ProcessManager
from attackmate.variablestore import VariableStore

output_logger = logging.getLogger('output')


@executor_factory.register_executor('remote')
class RemoteExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, varstore: VariableStore, cmdconfig=None):
        super().__init__(pm, varstore, cmdconfig)
        self.logger = logging.getLogger('playbook')
        # Client class is instantiated per command execution with server_url context and chached in
        # client_cache
        self._clients_cache: Dict[str, RemoteAttackMateClient] = {}

    def log_command(self, command: AttackMateRemoteCommand):
        self.logger.info(
            f"Executing REMOTE AttackMate command: Type='{command.type}', "
            f"RemoteCmd='{command.cmd}' on server {command.server_url}'"
        )
        remote_command_json = (
            command.remote_command.model_dump() if command.remote_command else ' '
        )
        output_logger.info(
            f"Remote Command'{remote_command_json}' sent to server {command.server_url}'"
        )

    async def _exec_cmd(self, command: AttackMateRemoteCommand) -> Result:
        try:
            client = self._get_remote_client(command)
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

    def _get_remote_client(self, command_config: AttackMateRemoteCommand) -> RemoteAttackMateClient:
        """Gets or creates a client instance for the given server URL."""
        server_url = self.varstore.substitute(command_config.server_url)
        if server_url in self._clients_cache:
            return self._clients_cache[server_url]
        else:
            self.logger.info(
                f'Creating new remote client for server: {server_url}'
            )
            new_remote_client = self._create_remote_client(command_config)
            self._clients_cache[server_url] = new_remote_client
        return self._clients_cache[server_url]

    def _create_remote_client(self, command_config: AttackMateRemoteCommand) -> RemoteAttackMateClient:
        """
        Creates and configures a new RemoteAttackMateClient
        """
        server_url = self.varstore.substitute(command_config.server_url)
        username = self.varstore.substitute(command_config.user) if command_config.user else None
        password = (
            self.varstore.substitute(command_config.password)
            if command_config.password else None
        )
        cacert = self.varstore.substitute(command_config.cacert) if command_config.cacert else None
        return RemoteAttackMateClient(
            server_url=server_url,
            username=username,
            password=password,  # noqa: E501
            cacert=cacert
        )

    def _dispatch_remote_command(
        self, client: 'RemoteAttackMateClient', command: AttackMateRemoteCommand
    ) -> Dict[str, Any]:
        """
        Dispatches the command to the appropriate client method.
        """
        debug = getattr(command, 'debug', False)
        self.logger.debug(f"Dispatching command '{command.cmd}' with debug={debug}")

        if command.cmd == 'execute_playbook' and command.playbook_yaml_content:
            with open(command.playbook_yaml_content, 'r') as f:
                yaml_content = f.read()
            response = client.execute_remote_playbook_yaml(yaml_content, debug=debug)

        elif command.cmd == 'execute_command':
            response = client.execute_remote_command(command.remote_command, debug=debug)

        else:
            raise ExecException(f"Unsupported remote command: '{command.cmd}'")

        return response if response is not None else {}

    def _process_response(self, response_data: Optional[Dict[str, Any]]) -> tuple:
        """
        Processes the raw response from the remote client to determine success,
        error message, return code, and stdout string.
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
        """Creates the final stdout string based on the execution result."""
        if error:
            # Prepend the error to the standard output if both exist
            header = f'Error: {error}'
            return f'{header}\n\nOutput/Response:\n{stdout}' if stdout else header

        if stdout is not None:
            return stdout

        return 'Operation completed successfully.' if success else 'Operation failed with no output.'
