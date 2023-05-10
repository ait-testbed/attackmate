from pymetasploit3.msfrpc import MsfRpcClient, MsfAuthError
from .baseexecutor import BaseExecutor, Result, ExecException
from .schemas import MsfSessionCommand, MsfModuleCommand, BaseCommand
from .msfsessionstore import MsfSessionStore
import atexit


class MsfModuleExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None, *, msfconfig=None, msfsessionstore: MsfSessionStore):
        self.msfconfig = msfconfig
        self.sessionstore = msfsessionstore
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

    def prepare_payload(self, command: MsfModuleCommand):
        self.logger.debug(f"Using payload: {command.payload}")
        if command.payload is None:
            return None
        if self.msf is not None:
            payload = self.msf.modules.use('payload', command.payload)
        else:
            raise ExecException("Problems with the metasploit connection")
        for option, setting in command.payload_options.items():
            try:
                payload[option] = setting
            except KeyError:
                raise ExecException(f"Payload option {option} is unknown")
        self.logger.debug(payload.options)
        return payload

    def prepare_exploit(self, command: MsfModuleCommand):
        exploit = None
        option: str = ""
        try:
            self.logger.debug(f"module_type: {command.module_type()}")
            self.logger.debug(f"module_path: {command.module_path()}")
            if self.msf is not None:
                exploit = self.msf.modules.use(command.module_type(),
                                               command.module_path())
            else:
                raise ExecException("Problems with the metasploit connection")
            self.logger.debug(exploit.description)
            for option, setting in command.options.items():
                exploit[option] = setting
            if command.session:
                session_id = self.sessionstore.get_session_by_name(command.session, self.msf.sessions)
                self.logger.debug(f"Using session-id: {session_id}")
                exploit['SESSION'] = int(session_id)
        except KeyError:
            raise ExecException(f"Module option {option} is unknown")
        except TypeError as e:
            raise ExecException(f"Module or Module Type is Unknown: {e}")
        if exploit.missing_required:
            raise ExecException(f"Missing required exploit options: {exploit.missing_required}")

        exploit.target = command.target
        return exploit

    def _exec_cmd(self, command: MsfModuleCommand) -> Result:
        if self.msf is None:
            raise ExecException("ConnectionError")

        exploit = self.prepare_exploit(command)
        payload = self.prepare_payload(command)

        if command.creates_session is not None:
            self.logger.debug("Command creates a msf-session")
            result = exploit.execute(payload=payload)
            self.logger.debug(result)
            self.sessionstore.wait_for_session(command.creates_session, result['uuid'], self.msf.sessions)
            return Result("", 0)
        cid = self.msf.consoles.console().cid
        output = self.msf.consoles.console(cid).run_module_with_output(exploit, payload=payload)
        return Result(output, 0)


class MsfSessionExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None, *, msfconfig=None, msfsessionstore: MsfSessionStore):
        self.msfconfig = msfconfig
        self.sessionstore = msfsessionstore
        self.msf = None
        atexit.register(self.cleanup)
        super().__init__(cmdconfig)

    def cleanup(self):
        self.logger.debug("Killing all Meterpreter-Sessions")
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
