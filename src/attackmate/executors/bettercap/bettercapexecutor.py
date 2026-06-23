from typing import Dict
from attackmate.processmanager import ProcessManager
from attackmate.variablestore import VariableStore
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.config import BettercapConfig
from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.schemas.bettercap import BettercapCommand
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.executors.bettercap.client import Client

from attackmate.executors.executor_factory import executor_factory


@executor_factory.register_executor('bettercap')
class BettercapExecutor(BaseExecutor):
    def __init__(
            self,
            pm: ProcessManager,
            cmdconfig=None,
            *,
            varstore: VariableStore,
            bettercap_config: Dict[str, BettercapConfig] = {}
    ):
        super().__init__(pm, varstore, cmdconfig)
        self.bettercap_config = bettercap_config
        self.client = Client('http://127.0.0.1:8081')
        self.client.user_agent('AttackMate')

    def setup_connection(self, command: BettercapCommand) -> None:
        if self.bettercap_config is None:
            raise ExecException('Bettercap config is missing')
        if not isinstance(self.bettercap_config, dict):
            raise ExecException('Bettercap config is not a dictionary')
        if command.connection is None:
            connection_name: str = next(iter(self.bettercap_config))
            self.logger.debug(f'Using default connection: {connection_name}')
        else:
            connection_name = command.connection
            self.logger.debug(f'Using connection: {connection_name}')
        if connection_name in self.bettercap_config:
            connection_config: BettercapConfig = self.bettercap_config[connection_name]
            self.client.server = connection_config.url
            if connection_config.username and connection_config.password:
                self.logger.debug('Using basic auth')
                self.client.basic_auth(connection_config.username, connection_config.password)
            if connection_config.cafile:
                self.logger.debug(f'Using cafile: {connection_config.cafile}')
                self.client.ca_file(connection_config.cafile)

    def log_command(self, command: BaseCommand):
        self.logger.info(
            f'Executing Bettercap Command: {command.cmd}'
        )

    async def _exec_cmd(self, command: BaseCommand) -> Result:
        try:
            if not isinstance(command, BettercapCommand):
                raise ExecException('Wrong command-type')
            self.setup_connection(command)
            if command.cmd in ['get_session_hid', 'get_session_ble', 'get_session_lan', 'get_session_wifi']:
                (code, headers, result) = getattr(self.client, command.cmd)(command.mac)
            elif command.cmd == 'get_file':
                (code, headers, result) = self.client.get_file(command.filename)
            elif command.cmd == 'post_api_session':
                (code, headers, result) = self.client.post_api_session(command.data)
            elif command.cmd == 'delete_api_events':
                (code, headers, result) = self.client.delete_api_events()
            else:
                (code, headers, result) = getattr(self.client, command.cmd)()

            self.logger.debug(headers)
            if code == 200:
                result = Result(result.decode(), 0)
            else:
                raise ExecException(f'Bettercap Command Status: {code} Returned: {result.decode()} ')
            return result
        except Exception as e:
            raise ExecException(e)
