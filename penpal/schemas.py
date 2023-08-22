from typing import List, Literal, Union, Optional, Dict
from pydantic import BaseModel

# https://stackoverflow.com/questions/71539448/using-different-pydantic-models-depending-on-the-value-of-fields


class BaseCommand(BaseModel):
    def list_template_vars(self) -> List[str]:
        """ Get a list of all variables that can be used as templates

        Returns a List with all member-names that can be used as
        templates for the VariableStore. Basically all members
        can be used that are strings where the value is not None.
        The member "type" is explicitly excluded.

        Returns
        -------
        List[str]
            List with names of all member-variables
        """
        template_vars: List[str] = []
        for k in self.__dict__.keys():
            tmp = getattr(self, k)
            if isinstance(tmp, str) and k != "type":
                template_vars.append(k)
        return template_vars

    error_if: Optional[str] = None
    error_if_not: Optional[str] = None
    loop_if: Optional[str] = None
    loop_if_not: Optional[str] = None
    loop_count: int = 3
    exit_on_error: bool = True
    cmd: str


class SleepCommand(BaseCommand):
    type: Literal['sleep']
    min_sec: int = 0
    seconds: int = 1
    random: bool = False
    cmd: str = "sleep"


class ShellCommand(BaseCommand):
    type: Literal['shell']


class DebugCommand(BaseCommand):
    type: Literal['debug']
    varstore: bool = False
    exit: bool = False


class RegExCommand(BaseCommand):
    type: Literal['regex']
    mode: Literal['search', 'split', 'findall'] = 'findall'
    input: str = 'RESULT_STDOUT'
    output: dict[str, str]


class SSHCommand(BaseCommand):
    type: Literal['ssh']
    hostname: Optional[str]
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]
    passphrase: Optional[str]
    key_filename: Optional[str]
    creates_session: Optional[str]
    session: Optional[str]
    clear_cache: bool = False
    timeout: float = 60
    jmp_hostname: Optional[str]
    jmp_port: Optional[int]
    jmp_username: Optional[str]


class MsfSessionCommand(BaseCommand):
    type: Literal['msf-session']
    cmd: str
    stdapi: bool = False
    write: bool = False
    read: bool = False
    session: str
    end_str: Optional[str]


class MsfModuleCommand(BaseCommand):
    cmd: str
    type: Literal['msf-module']
    target: int = 0
    creates_session: Optional[str]
    session: Optional[str]
    payload: Optional[str]
    options: Dict[str, str] = {}
    payload_options: Dict[str, str] = {}

    def is_interactive(self):
        if self.interactive is not None:
            return self.interactive
        if self.module_type() == "exploit":
            return True
        else:
            return False

    def module_type(self):
        if self.cmd is None:
            return None
        return self.cmd.split("/")[0]

    def module_path(self):
        if self.cmd is None:
            return None
        return "/".join(self.cmd.split("/")[1:])


class CommandConfig(BaseModel):
    loop_sleep: int = 5


class SliverConfig(BaseModel):
    config_file: Optional[str] = None


class MsfConfig(BaseModel):
    password: Optional[str] = None
    ssl: bool = True
    port: int = 55553
    server: Optional[str] = "127.0.0.1"
    uri: Optional[str] = "/api/"


class SliverHttpsListenerCommand(BaseCommand):
    type: Literal['sliver']
    host: str = "0.0.0.0"


class SliverImplantCommand(BaseCommand):
    type: Literal['sliver-implant']
    target: Literal[
            'darwin/amd64',
            'darwin/arm64',
            'linux/386',
            'linux/amd64',
            'windows/386',
            'windows/amd64'] = 'linux/amd64'
    c2url: str
    format: Literal[
            'EXECUTABLE',
            'SERVICE',
            'SHARED_LIB',
            'SHELLCODE'] = 'EXECUTABLE'
    name: str
    filepath: Optional[str]


class Config(BaseModel):
    sliver_config: SliverConfig = SliverConfig(config_file=None)
    msf_config: MsfConfig = MsfConfig(password=None)
    cmd_config: CommandConfig = CommandConfig(loop_sleep=5)
    vars: Optional[Dict[str, str]] = None
    commands: List[Union[
                         ShellCommand,
                         MsfModuleCommand,
                         MsfSessionCommand,
                         SleepCommand,
                         SSHCommand,
                         DebugCommand,
                         RegExCommand,
                         SliverImplantCommand,
                         SliverHttpsListenerCommand]]
