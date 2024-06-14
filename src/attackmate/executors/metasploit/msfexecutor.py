from pymetasploit3.msfrpc import MsfRpcClient, MsfAuthError

from typing import Optional
from attackmate.variablestore import VariableStore
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.metasploit import MsfModuleCommand
from attackmate.executors.metasploit.msfsessionstore import MsfSessionStore
from attackmate.processmanager import ProcessManager
from multiprocessing import Manager
from multiprocessing.queues import JoinableQueue


class MsfModuleExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *,
                 varstore: VariableStore,
                 msfconfig=None,
                 msfsessionstore: MsfSessionStore):
        self.msfconfig = msfconfig
        self.sessionstore = msfsessionstore
        self.msf = None
        super().__init__(pm, varstore, cmdconfig)

    def _create_queue(self) -> Optional[JoinableQueue]:
        if self.sessionstore.queue:
            return self.sessionstore.queue
        if not self.manager:
            self.manager = Manager()
            self.sessionstore.queue = self.manager.JoinableQueue()  # type: ignore
        return self.sessionstore.queue

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
        self.logger.info(f"Executing Msf-Module: '{command.cmd}'")

    def prepare_payload(self, command: MsfModuleCommand):
        self.logger.debug(f'Using payload: {command.payload}')
        if command.payload is None:
            return None
        if self.msf is not None:
            try:
                payload = self.msf.modules.use('payload', command.payload)
            except TypeError:
                raise ExecException(f'Payload {command.payload} seems to be incorrect')
        else:
            raise ExecException('Problems with the metasploit connection')
        for option, setting in command.payload_options.items():
            try:
                payload[option] = setting
            except KeyError:
                raise ExecException(f'Payload option {option} is unknown')
        self.logger.debug(payload.options)
        return payload

    def prepare_exploit(self, command: MsfModuleCommand):
        exploit = None
        option: str = ''
        try:
            self.logger.debug(f'module_type: {command.module_type()}')
            self.logger.debug(f'module_path: {command.module_path()}')
            if self.msf is not None:
                exploit = self.msf.modules.use(command.module_type(),
                                               command.module_path())
            else:
                raise ExecException('Problems with the metasploit connection')
            self.logger.debug(exploit.description)
            for option, setting in command.options.items():
                if setting.isnumeric():
                    exploit[option] = int(setting)
                if setting.lower() in ['true', 'false', '1', '0', 'y', 'n', 'yes', 'no']:
                    exploit[option] = CmdVars.variable_to_bool(option, setting)
                else:
                    exploit[option] = setting
            if command.session:
                session_id = self.sessionstore.get_session_by_name(command.session, self.msf.sessions)
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

    def _exec_cmd(self, command: MsfModuleCommand) -> Result:
        if self.msf is None:
            raise ExecException('ConnectionError')

        exploit = self.prepare_exploit(command)
        payload = self.prepare_payload(command)

        if command.creates_session is not None:
            self.logger.debug('Command creates a msf-session')
            result = exploit.execute(payload=payload)
            self.logger.debug(result)
            self.logger.debug(command.module_path())
            if command.module_path() == 'multi/manage/shell_to_meterpreter':
                self.logger.debug('Waiting for increased session..')
                self.sessionstore.wait_for_increased_session(command.creates_session,
                                                             result['uuid'],
                                                             self.msf.sessions,
                                                             self.child_queue)
            else:
                self.sessionstore.wait_for_session(command.creates_session,
                                                   result['uuid'],
                                                   self.msf.sessions, self.child_queue)
            return Result('', 0)
        cid = self.msf.consoles.console().cid
        output = self.msf.consoles.console(cid).run_module_with_output(exploit, payload=payload)
        return Result(output, 0)
