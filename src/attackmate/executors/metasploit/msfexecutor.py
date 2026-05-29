from typing import Optional, Dict
from attackmate.variablestore import VariableStore
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.metasploit import MsfModuleCommand
from attackmate.schemas.config import MsfConfig
from attackmate.executors.metasploit.msfsessionstore import MsfSessionStore
from attackmate.executors.metasploit.msfclientmixin import MsfClientMixin
from attackmate.processmanager import ProcessManager
from multiprocessing.managers import BaseManager
from multiprocessing import Manager
from multiprocessing.queues import JoinableQueue
from attackmate.executors.executor_factory import executor_factory
from pymetasploit3.msfrpc import MsfRpcClient


@executor_factory.register_executor('msf-module')
class MsfModuleExecutor(MsfClientMixin, BaseExecutor):
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
        self.manager: Optional[BaseManager] = None
        super().__init__(pm, varstore, cmdconfig)

    def _create_queue(self) -> Optional[JoinableQueue]:
        if self.sessionstore.queue:
            return self.sessionstore.queue
        if not self.manager:
            self.manager = Manager()
            self.sessionstore.queue = self.manager.JoinableQueue()  # type: ignore
        return self.sessionstore.queue

    def log_command(self, command: BaseCommand):
        self.logger.info(f"Executing Msf-Module: '{command.cmd}'")

    def prepare_payload(self, command: MsfModuleCommand, msf: MsfRpcClient):
        self.logger.debug(f'Using payload: {command.payload}')
        if command.payload is None:
            return None
        try:
            payload = msf.modules.use('payload', command.payload)
        except TypeError:
            raise ExecException(f'Payload {command.payload} seems to be incorrect')
        for option, setting in command.payload_options.items():
            try:
                payload[option] = setting
            except KeyError:
                raise ExecException(f'Payload option {option} is unknown')
        self.logger.debug(payload.options)
        return payload

    def prepare_exploit(self, command: MsfModuleCommand, msf: MsfRpcClient, conn_name: str):
        exploit = None
        option: str = ''
        try:
            self.logger.debug(f'module_type: {command.module_type()}')
            self.logger.debug(f'module_path: {command.module_path()}')
            exploit = msf.modules.use(command.module_type(), command.module_path())
            self.logger.debug(exploit.description)
            for option, setting in command.options.items():
                if setting.isnumeric():
                    exploit[option] = int(setting)
                    continue
                if setting.lower() in ['true', 'false', '1', '0', 'y', 'n', 'yes', 'no']:
                    exploit[option] = CmdVars.variable_to_bool(option, setting)
                else:
                    exploit[option] = setting
            if command.session:
                session_id = self.sessionstore.get_session_by_name(conn_name, command.session, msf.sessions)
                self.logger.debug(f'Using session-id: {session_id}')
                exploit['SESSION'] = int(session_id)
        except KeyError:
            raise ExecException(f'Module option {option} is unknown')
        except TypeError as e:
            raise ExecException(f'Module or Module Type is Unknown: {e}')
        if exploit.missing_required:
            raise ExecException(f'Missing required exploit options: {exploit.missing_required}')
        exploit.target = CmdVars.variable_to_int('target', command.target)
        return exploit

    async def _exec_cmd(self, command: MsfModuleCommand) -> Result:
        conn_name = self._resolve_connection(command)
        msf = self._get_client(conn_name)

        exploit = self.prepare_exploit(command, msf, conn_name)
        payload = self.prepare_payload(command, msf)

        if command.creates_session is not None:
            self.logger.debug('Command creates a msf-session')
            result = exploit.execute(payload=payload)
            self.logger.debug(result)
            self.logger.debug(command.module_path())
            if command.module_path() == 'multi/manage/shell_to_meterpreter':
                self.logger.debug('Waiting for increased session..')
                self.sessionstore.wait_for_increased_session(
                    conn_name, command.creates_session, result['uuid'], msf.sessions, self.child_queue
                )
            else:
                self.sessionstore.wait_for_session(
                    conn_name, command.creates_session, result['uuid'], msf.sessions, self.child_queue
                )
            return Result('', 0)
        cid = msf.consoles.console().cid
        output = msf.consoles.console(cid).run_module_with_output(exploit, payload=payload)
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
