from pymetasploit3.msfrpc import MsfRpcClient, MsfAuthError
from .baseexecutor import BaseExecutor, Result
from .schemas import MsfModuleCommand, BaseCommand


class MsfModuleExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None, *, msfconfig=None):
        self.msfconfig = msfconfig
        self.msf = None
        super().__init__(cmdconfig)

    def connect(self, msfconfig=None):
        try:
            self.msf = MsfRpcClient(**msfconfig.dict())
        except IOError as e:
            self.logger.error(e)
            self.msf = None
        except MsfAuthError as e:
            self.logger.error(e)
            self.msf = None

    def log_command(self, command: BaseCommand):
        if self.msf is None:
            self.logger.debug("Connecting to msf-server...")
            self.connect(self.msfconfig)
        self.logger.info(f"Executing Msf-Module: '{command.cmd}'")

    def _exec_cmd(self, command: MsfModuleCommand) -> Result:
        if self.msf is None:
            return Result("ConnectionError", 1)

        self.logger.debug(self.msf.sessions.list)
        exploit = self.msf.modules.use(command.module_type, command.cmd)
        self.logger.debug(exploit.description)
        try:
            for option, setting in command.options.items():
                exploit[option] = setting
        except KeyError:
            return Result(f"Module option {option} is unknown", 1)

        self.logger.debug(f"Using payload: {command.payload}")
        if command.payload is None:
            payload = None
        else:
            payload = self.msf.modules.use('payload', command.payload)
            try:
                for option, setting in command.payload_options.items():
                    payload[option] = setting
            except KeyError:
                return Result(f"Payload option {option} is unknown", 1)
            self.logger.debug(payload.options)

        result = exploit.execute(payload=payload)
        self.logger.debug(result)
        self.logger.debug(self.msf.sessions.list)
        return Result("", 0)
