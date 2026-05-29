import atexit

from typing import Dict
from attackmate.variablestore import VariableStore
from attackmate.executors.metasploit.msfsessionstore import MsfSessionStore
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.metasploit import MsfSessionCommand
from attackmate.schemas.config import MsfConfig
from attackmate.executors.metasploit.msfclientmixin import MsfClientMixin
from attackmate.execexception import ExecException
from attackmate.processmanager import ProcessManager
from attackmate.executors.executor_factory import executor_factory
from pymetasploit3.msfrpc import MsfRpcClient


@executor_factory.register_executor('msf-session')
class MsfSessionExecutor(MsfClientMixin, BaseExecutor):
    def __init__(
        self,
        pm: ProcessManager,
        cmdconfig=None,
        *,
        varstore: VariableStore,
        msf_config: Dict[str, MsfConfig] = {},
        msfsessionstore: MsfSessionStore,
    ):
        self.msf_config = msf_config
        self._msf_clients: Dict[str, MsfRpcClient] = {}
        self.sessionstore = msfsessionstore
        atexit.register(self.cleanup)
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: BaseCommand):
        self.logger.info(f"Executing Msf-Session-Command: '{command.cmd}'")

    async def _exec_cmd(self, command: MsfSessionCommand) -> Result:
        conn_name = self._resolve_connection(command)
        msf = self._get_client(conn_name)

        session_id = self.sessionstore.get_session_by_name(command.session, msf.sessions)
        self.logger.debug(f'Using session-id: {session_id}')
        return_empty = False

        try:
            if command.stdapi:
                self.logger.info('Loading stapi')
                msf.sessions.session(session_id).write('load stdapi')
            if command.write:
                self.logger.info('Writing raw-data in msf-session')
                msf.sessions.session(session_id).write(command.cmd)
                output = ''
                return_empty = True
            if command.read:
                self.logger.info('Reading raw-data in msf-session')
                output = msf.sessions.session(session_id).read()
                return Result(output, 0)

            if not return_empty:
                self.logger.info('Executing a msf-command')
                try:
                    output = msf.sessions.session(session_id).run_with_output(
                        command.cmd, command.end_str
                    )
                except TypeError:
                    self.logger.debug('Fallback: First raw-write again and then raw-read data in msf-session')
                    msf.sessions.session(session_id).write(command.cmd)
                    output = msf.sessions.session(session_id).read()

        except KeyError as e:
            self.logger.debug(msf.sessions.list)
            self.logger.debug(session_id)
            raise ExecException(e)
        return Result(output, 0)

    def cleanup(self):
        for conn_name, msf in self._msf_clients.items():
            self.logger.debug(f'Killing all Meterpreter sessions for connection: {conn_name}')
            active_sessions = msf.sessions.list
            if active_sessions:
                for session_id, session_data in active_sessions.items():
                    try:
                        self.logger.debug(f'Stopping msf session {session_id}')
                        msf.sessions.session(session_id).stop()
                        self.logger.info(f'Msf session {session_id} stopped successfully.')
                    except Exception as e:
                        self.logger.error(f'Failed to stop msf session {session_id}: {str(e)}')
            else:
                self.logger.debug(f'No active msf sessions found for connection: {conn_name}')
