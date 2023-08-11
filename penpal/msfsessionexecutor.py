import atexit

from penpal.variablestore import VariableStore
from .baseexecutor import BaseExecutor, Result, ExecException
from pymetasploit3.msfrpc import MsfRpcClient, MsfAuthError
from .schemas import MsfSessionCommand, BaseCommand
from .msfsessionstore import MsfSessionStore


class MsfSessionExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None, *,
                 varstore: VariableStore,
                 msfconfig=None,
                 msfsessionstore: MsfSessionStore):
        self.msfconfig = msfconfig
        self.sessionstore = msfsessionstore
        self.msf = None
        atexit.register(self.cleanup)
        super().__init__(varstore, cmdconfig)

    def cleanup(self):
        self.logger.debug("Killing all Meterpreter-Sessions")
        if self.msf is not None:
            for session_id in self.msf.sessions.list.keys():
                self.msf.sessions.session(session_id).stop()

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
        self.logger.info(f"Executing Msf-Session-Command: '{command.cmd}'")

    def _exec_cmd(self, command: MsfSessionCommand) -> Result:
        if self.msf is None:
            raise ExecException("ConnectionError")

        session_id = self.sessionstore.get_session_by_name(command.session, self.msf.sessions)
        self.logger.debug(f"Using session-id: {session_id}")
        try:
            if command.read:
                self.logger.info("Reading raw-data in msf-session")
                output = self.msf.sessions.session(session_id).read()
                return Result(output, 0)

            if command.stdapi:
                self.logger.info("Loading stapi")
                self.msf.sessions.session(session_id).write('load stdapi')
            if command.write:
                self.logger.info("Writing raw-data in msf-session")
                self.msf.sessions.session(session_id).write(command.cmd)
                output = ""
            else:
                self.logger.info("Executing a msf-command")
                output = self.msf.sessions.session(session_id).run_with_output(command.cmd, command.end_str)
        except KeyError as e:
            self.logger.debug(self.msf.sessions.list)
            self.logger.debug(session_id)
            raise ExecException(e)
        return Result(output, 0)
