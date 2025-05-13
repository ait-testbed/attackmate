import logging
import os
import yaml
import json
from typing import Dict, Any, Optional

from attackmate.executors.executor_factory import executor_factory

from attackmate.remote_client import RemoteAttackMateClient
from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.schemas.remote import AttackMateRemoteCommand
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.processmanager import ProcessManager
from attackmate.variablestore import VariableStore


@executor_factory.register_executor('remote')
class RemoteExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, varstore: VariableStore, cmdconfig=None):
        super().__init__(pm, varstore, cmdconfig)
        # self.client is instantiated per command execution
        self.logger = logging.getLogger('playbook')
        # Client class is instantiated per command execution with server_url context
        self._clients_cache: Dict[str, RemoteAttackMateClient] = {}  # Cache clients per server_url

    def log_command(self, command: AttackMateRemoteCommand):
        self.logger.info(
            f"Executing REMOTE AttackMate command: Type='{command.type}', "
            f"RemoteCmd='{command.cmd}' on server {command.server_url}'"
        )

    def _get_client(self, command_config: AttackMateRemoteCommand) -> RemoteAttackMateClient:
        """Gets or creates a client instance for the given server URL."""
        server_url = self.varstore.substitute(command_config.server_url) # maybe better way?
        if server_url not in self._clients_cache:
            self.logger.info(f"Creating new remote client for server: {server_url}")
            # Substitute user/password from local varstore if they are variables
            user = self.varstore.substitute(command_config.user) if command_config.user else None
            password = self.varstore.substitute(command_config.password) if command_config.password else None
            cacert = self.varstore.substitute(command_config.cacert) if command_config.cacert else None

            self._clients_cache[server_url] = RemoteAttackMateClient(
                server_url=server_url,
                cacert=cacert,
                username=user,
                password=password
                # maybe make Timeout configurable via AttackMateRemoteCommand?
            )
        return self._clients_cache[server_url]

    def _exec_cmd(self, command: AttackMateRemoteCommand) -> Result:
        client = self._get_client(command)
        response_data: Optional[Dict[str, Any]] = None
        error_message: Optional[str] = None
        success: bool = False
        stdout_str: Optional[str] = None
        return_code: int = 1 # Default to error

        # TODO make this properly configurable in AttackMateRemoteCommand for logging on server
        api_call_debug_flag = False
        if hasattr(command, 'debug') and isinstance(command.debug, bool): #  add 'debug' as parameter to AttackMateRemoteCommand
            api_call_debug_flag = command.debug

        try:
            if command.cmd == 'execute_playbook_yaml':
                # Substitute local vars into playbook content before sending?
                # TODO decide on this, or if substitution happens only on the server side

                try:
                    with open(command.playbook_yaml_content, 'r') as f:
                        yaml_content = f.read()
                        # TODO decide on varibale subsitution here
                        #  final_yaml_content = self.varstore.substitute(yaml_content)
                        response_data = client.execute_remote_playbook_yaml(yaml_content, debug=api_call_debug_flag)
                except Exception as e:
                    raise ExecException(f"Failed to read local file '{command.playbook_yaml_content}': {e}")

            elif command.cmd == 'execute_playbook_file':
                response_data = client.execute_remote_playbook_file(command.playbook_file_path,
                                                                    debug=api_call_debug_flag)

            elif command.cmd == 'execute_command':
                response_data = client.execute_remote_command(
                    command_pydantic_model=command.remote_command,
                    debug=api_call_debug_flag
                )

            # Process response
            if response_data:
                cmd_result = response_data.get('result', {})
                if cmd_result:
                    success = cmd_result.get('success', False)
                    stdout_str = cmd_result.get('stdout')
                    return_code = cmd_result.get('returncode', 1 if not success else 0)
                    if not success and 'error_message' in cmd_result:
                        error_message = cmd_result['error_message']
                elif 'success' in response_data: # For playbook responses
                    success = response_data.get('success', False)
                    stdout_str = json.dumps(response_data, indent=2) # Whole response as stdout
                    return_code = 0 if success else 1
                    if not success:
                        error_message = response_data.get('message')
                else:
                    error_message = 'Received unexpected response structure from remote server.'
                    stdout_str = json.dumps(response_data, indent=2)
                    success = False
                    return_code = 1

            else:  # No response_data from client call
                error_message = 'No response received from remote server (client communication failed).'
                success = False
                return_code = 1

        except ExecException:
            raise
        except Exception as e:
            error_message = f"Remote executor encountered an error: {e}"
            self.logger.error(error_message, exc_info=True)
            success = False
            return_code = 1

        # Finalize output, executir return whatever the remote server returns
        if error_message and stdout_str and 'Error:' not in stdout_str:
            stdout_str = f"Error: {error_message}\n\nOutput/Response:\n{stdout_str}"
        elif error_message:
            stdout_str = f"Error: {error_message}"
        elif stdout_str is None:
            stdout_str = 'Operation completed.' if success else 'Operation failed.'

        return Result(stdout_str, return_code if return_code is not None else (0 if success else 1))
