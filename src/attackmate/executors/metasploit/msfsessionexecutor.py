import atexit

from pymetasploit3.msfrpc import MsfRpcClient, MsfAuthError
from attackmate.variablestore import VariableStore
from attackmate.executors.metasploit.msfsessionstore import MsfSessionStore
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.metasploit import MsfSessionCommand
from attackmate.processmanager import ProcessManager


class MsfSessionExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *,
                 varstore: VariableStore,
                 msfconfig=None,
                 msfsessionstore: MsfSessionStore):
        self.msfconfig = msfconfig
        self.sessionstore = msfsessionstore
        self.msf = None
        atexit.register(self.cleanup)
        super().__init__(pm, varstore, cmdconfig)

    def cleanup(self):
        if self.msf is not None:
            self.logger.debug('Killing all Meterpreter-Sessions')
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
            self.logger.debug('Connecting to msf-server...')
            self.connect(self.msfconfig)
        self.logger.info(f"Executing Msf-Session-Command: '{command.cmd}'")

    def _exec_cmd(self, command: MsfSessionCommand) -> Result:
        if self.msf is None:
            raise ExecException('ConnectionError')

        session_id = self.sessionstore.get_session_by_name(command.session, self.msf.sessions)
        self.logger.debug(f'Using session-id: {session_id}')
        return_empty = False

        try:

            if command.stdapi:
                self.logger.info('Loading stapi')
                self.msf.sessions.session(session_id).write('load stdapi')
            if command.write:
                self.logger.info('Writing raw-data in msf-session')
                self.msf.sessions.session(session_id).write(command.cmd)
                output = ''
                return_empty = True
            if command.read:
                self.logger.info('Reading raw-data in msf-session')
                output = self.msf.sessions.session(session_id).read()
                return Result(output, 0)

            if not return_empty:
                self.logger.info('Executing a msf-command')
                try:
                    output = self.msf.sessions.session(session_id).run_with_output(command.cmd,
                                                                                   command.end_str)
                except TypeError:
                    self.logger.debug('Fallback: First raw-write again and then raw-read data in msf-session')
                    self.msf.sessions.session(session_id).write(command.cmd)
                    output = self.msf.sessions.session(session_id).read()

        except KeyError as e:
            self.logger.debug(self.msf.sessions.list)
            self.logger.debug(session_id)
            raise ExecException(e)
        return Result(output, 0)
