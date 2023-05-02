from pymetasploit3.msfrpc import MsfRpcClient
from .baseexecutor import BaseExecutor, Result
from .schemas import MsfModuleCommand, BaseCommand


class MsfModuleExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None, *, msfconfig=None):
        self.msfconfig = msfconfig
        try:
            self.password = msfconfig.password
        except AttributeError:
            self.password = None
        print(msfconfig)
        self.msf = None
        super().__init__(cmdconfig)

    def connect(self, msfconfig=None):
        self.msf = MsfRpcClient(**msfconfig.dict())

    def log_command(self, command: BaseCommand):
        if self.msf is None:
            self.logger.debug("Connecting to msf-server...")
            self.connect(self.msfconfig)
        self.logger.info(f"Executing Msf-Module: '{command.cmd}'")

    def _exec_cmd(self, command: MsfModuleCommand) -> Result:
        exploit = self.msf.modules.use(command.module_type, command.cmd)
        self.logger.debug(exploit.description)
        exploit['RHOSTS'] = command.options['RHOSTS']
        self.logger.debug(f"Using payload: {command.payload}")
        payload = self.msf.modules.use('payload', command.payload)
        payload['LHOST'] = command.options['LHOST']
        self.logger.debug(payload.options)
        result = exploit.execute(payload=payload)
        self.logger.debug(result)
        self.logger.debug(self.msf.sessions.list)
        return Result("", 0)
