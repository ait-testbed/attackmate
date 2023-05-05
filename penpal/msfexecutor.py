from pymetasploit3.msfrpc import MsfRpcClient, MsfAuthError
from .baseexecutor import BaseExecutor, Result, ExecException
from .schemas import MsfSessionCommand, MsfModuleCommand, BaseCommand
import time
import atexit


class MsfModuleExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None, *, msfconfig=None):
        self.msfconfig = msfconfig
        self.msf = None
        self.last_uuid = None
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
        payload = self.msf.modules.use('payload', command.payload)
        for option, setting in command.payload_options.items():
            try:
                payload[option] = setting
            except KeyError:
                raise ExecException(f"Payload option {option} is unknown")
        self.logger.debug(payload.options)
        return payload

    def prepare_exploit(self, command: MsfModuleCommand):
        exploit = None
        try:
            self.logger.debug(f"module_type: {command.module_type()}")
            self.logger.debug(f"module_path: {command.module_path()}")
            exploit = self.msf.modules.use(command.module_type(),
                                           command.module_path())
            self.logger.debug(exploit.description)
            for option, setting in command.options.items():
                exploit[option] = setting
        except KeyError:
            raise ExecException(f"Module option {option} is unknown")
        except TypeError:
            raise ExecException("Module or Module Type is Unknown")
        if exploit.missing_required:
            raise ExecException(f"Missing required exploit options: {exploit.missing_required}")

        exploit.target = command.target
        return exploit

    def _exec_cmd(self, command: MsfModuleCommand) -> Result:
        if self.msf is None:
            raise ExecException("ConnectionError")

        exploit = self.prepare_exploit(command)
        payload = self.prepare_payload(command)

        self.logger.debug(f"interactive: {command.is_interactive()}")
        if command.is_interactive():
            result = exploit.execute(payload=payload)
            self.last_uuid = result['uuid']
            self.logger.debug(result)
            return Result("", 0)
        cid = self.msf.consoles.console().cid
        output = self.msf.consoles.console(cid).run_module_with_output(exploit, payload=payload)
        return Result(output, 0)


class MsfSessionExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None, *, msfconfig=None):
        self.msfconfig = msfconfig
        self.msf = None
        self.last_uuid = None
        self.session_id = None
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

    def get_session_id(self, command: MsfSessionCommand):
        seconds = 20
        session_id = None

        if self.session_id is not None:
            return self.session_id

        if command.session_id is not None:
            return command.session_id

        self.logger.debug(f"Sessions: {self.msf.sessions.list}")
        if self.last_uuid is not None:
            while session_id is None:
                self.logger.debug(f"Waiting Sessions: {self.msf.sessions.list}")
                for sid, item in self.msf.sessions.list.items():
                    if item['exploit_uuid'] == self.last_uuid:
                        session_id = sid
        else:
            while session_id is None:
                if len(list(self.msf.sessions.list.keys())) > 0:
                    session_id = list(self.msf.sessions.list.keys())[0]
        self.logger.debug(f"Waiting {seconds} seconds for session to get ready")
        time.sleep(seconds)
        return session_id

    def log_command(self, command: BaseCommand):
        if self.msf is None:
            self.logger.debug("Connecting to msf-server...")
            self.connect(self.msfconfig)
        self.logger.info(f"Executing Msf-Session-Command: '{command.cmd}'")

    def _exec_cmd(self, command: MsfSessionCommand) -> Result:
        if self.msf is None:
            raise ExecException("ConnectionError")

        self.session_id = self.get_session_id(command)
        self.logger.debug(f"Using session-id: {self.session_id}")
        if command.stdapi:
            self.logger.info("Loading stapi")
            self.msf.sessions.session(self.session_id).write('load stdapi')
        if command.write:
            self.logger.info("Writing raw-data in msf-session")
            self.msf.sessions.session(self.session_id).write(command.cmd)
            output = ""
        else:
            self.logger.info("Executing a msf-command")
            output = self.msf.sessions.session(self.session_id).run_with_output(command.cmd)
        return Result(output, 0)
