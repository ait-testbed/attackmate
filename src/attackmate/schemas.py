from typing import List, Literal, Union, Optional, Dict
from pydantic import BaseModel, Field, validator

# https://stackoverflow.com/questions/71539448/using-different-pydantic-models-depending-on-the-value-of-fields

VAR_PATTERN = r'^\$[$a-zA-Z0-9_]+$|^[0-9]+$'


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
            if isinstance(tmp, (str, dict, list)) and k != 'type':
                template_vars.append(k)
        return template_vars

    @validator('background')
    def bg_not_implemented_yet(cls, v):
        if cls in (SSHCommand, SFTPCommand, MsfSessionCommand, IncludeCommand):
            raise ValueError('background mode is unsupported for this command')
        return v

    only_if: Optional[str] = None
    error_if: Optional[str] = None
    error_if_not: Optional[str] = None
    loop_if: Optional[str] = None
    loop_if_not: Optional[str] = None
    loop_count: str = Field(pattern=VAR_PATTERN, default='3')
    exit_on_error: bool = True
    save: Optional[str] = None
    cmd: str
    background: bool = False
    kill_on_exit: bool = True


class SleepCommand(BaseCommand):
    type: Literal['sleep']
    min_sec: str = Field(pattern=VAR_PATTERN, default='0')
    seconds: str = Field(pattern=VAR_PATTERN, default='1')
    random: bool = False
    cmd: str = 'sleep'


class ShellCommand(BaseCommand):
    type: Literal['shell']


class SetVarCommand(BaseCommand):
    type: Literal['setvar']
    variable: str
    encoder: Optional[str] = None


class IncludeCommand(BaseCommand):
    type: Literal['include']
    local_path: str
    cmd: str = 'include commands'


class WebServCommand(BaseCommand):
    type: Literal['webserv']
    cmd: str = 'HTTP-GET'
    local_path: str
    port: str = Field(pattern=VAR_PATTERN, default='8000')
    address: str = '0.0.0.0'  # nosec


class FatherCommand(BaseCommand):
    type: Literal['father']
    cmd: Literal['generate'] = 'generate'
    gid: str = '1337'
    srcport: str = '54321'
    epochtime: str = '0000000000'
    env_var: str = 'lobster'
    file_prefix: str = 'lobster'
    preload_file: str = 'ld.so.preload'
    hiddenport: str = 'D431'
    shell_pass: str = 'lobster'
    install_path: str = '/lib/selinux.so.3'
    local_path: Optional[str]
    arch: Literal['amd64'] = 'amd64'
    build_command: str = 'make'


class TempfileCommand(BaseCommand):
    type: Literal['mktemp']
    cmd: Literal['file', 'dir'] = 'file'
    variable: str


class DebugCommand(BaseCommand):
    type: Literal['debug']
    varstore: bool = False
    exit: bool = False
    cmd: str = ''


class RegExCommand(BaseCommand):
    type: Literal['regex']
    mode: Literal['search', 'split', 'findall'] = 'findall'
    input: str = 'RESULT_STDOUT'
    output: dict[str, str]


class SSHBase(BaseCommand):
    hostname: Optional[str]
    port: Optional[str] = Field(pattern=VAR_PATTERN, default=None)
    username: Optional[str]
    password: Optional[str]
    passphrase: Optional[str]
    key_filename: Optional[str]
    creates_session: Optional[str]
    session: Optional[str]
    clear_cache: bool = False
    timeout: float = 60
    jmp_hostname: Optional[str]
    jmp_port: Optional[str] = Field(pattern=VAR_PATTERN, default=None)
    jmp_username: Optional[str]


class SSHCommand(SSHBase):
    type: Literal['ssh']
    interactive: bool = False
    validate_prompt: bool = True
    command_timeout: str = Field(pattern=VAR_PATTERN, default='15')
    prompts: List[str] = ['$ ', '# ', '> ']


class SFTPCommand(SSHBase):
    type: Literal['sftp']
    cmd: Literal['get', 'put']
    remote_path: str
    local_path: str
    mode: Optional[str]


class MsfSessionCommand(BaseCommand):
    type: Literal['msf-session']
    cmd: str
    stdapi: bool = False
    write: bool = False
    read: bool = False
    session: str
    end_str: Optional[str]


class MsfPayloadCommand(BaseCommand):
    type: Literal['msf-payload']
    cmd: str
    format: str = 'raw'
    badchars: str = ''
    force_encode: bool = False
    encoder: str = ''
    template: Optional[str] = None
    platform: Optional[str] = None
    keep_template_working: bool = False
    nopsled_size: str = Field(pattern=VAR_PATTERN, default='0')
    iter: str = Field(pattern=VAR_PATTERN, default='0')
    payload_options: Dict[str, str] = {}
    local_path: Optional[str]


class MsfModuleCommand(BaseCommand):
    cmd: str
    type: Literal['msf-module']
    target: str = Field(pattern=VAR_PATTERN, default='0')
    creates_session: Optional[str]
    session: Optional[str]
    payload: Optional[str]
    options: Dict[str, str] = {}
    payload_options: Dict[str, str] = {}

    def is_interactive(self):
        if self.interactive is not None:
            return self.interactive
        if self.module_type() == 'exploit':
            return True
        else:
            return False

    def module_type(self):
        if self.cmd is None:
            return None
        return self.cmd.split('/')[0]

    def module_path(self):
        if self.cmd is None:
            return None
        return '/'.join(self.cmd.split('/')[1:])


class HttpClientCommand(BaseCommand):
    type: Literal['http-client']
    cmd: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'] = 'GET'
    url: str
    output_headers: bool = False
    headers: Optional[Dict[str, str]]
    cookies: Optional[Dict[str, str]]
    data: Optional[Dict[str, str]]
    local_path: Optional[str]
    useragent: str = 'AttackMate'
    follow: bool = False
    verify: bool = False
    http2: bool = False


class CommandConfig(BaseModel):
    loop_sleep: int = 5


class SliverConfig(BaseModel):
    config_file: Optional[str] = None


class MsfConfig(BaseModel):
    password: Optional[str] = None
    ssl: bool = True
    port: int = 55553
    server: Optional[str] = '127.0.0.1'
    uri: Optional[str] = '/api/'


class SliverHttpsListenerCommand(BaseCommand):
    type: Literal['sliver']
    cmd: Literal['start_https_listener']
    host: str = '0.0.0.0'  # nosec
    port: str = Field(pattern=VAR_PATTERN, default='443')
    domain: str = ''
    website: str = ''
    acme: bool = False
    persistent: bool = False
    enforce_otp: bool = True
    randomize_jarm: bool = True
    long_poll_timeout: str = Field(pattern=VAR_PATTERN, default='1')
    long_poll_jitter: str = Field(pattern=VAR_PATTERN, default='2')
    timeout: str = Field(pattern=VAR_PATTERN, default='60')


class SliverGenerateCommand(BaseCommand):
    type: Literal['sliver']
    cmd: Literal['generate_implant']
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
    IsBeacon: bool = False
    BeaconInterval: str = Field(pattern=VAR_PATTERN, default='120')
    RunAtLoad: bool = False
    Evasion: bool = False


class SliverSessionCommand(BaseCommand):
    type: Literal['sliver-session']
    session: str
    beacon: bool = False


class SliverSessionCDCommand(SliverSessionCommand):
    cmd: Literal['cd']
    remote_path: str


class SliverSessionMKDIRCommand(SliverSessionCommand):
    cmd: Literal['mkdir']
    remote_path: str


class SliverSessionDOWNLOADCommand(SliverSessionCommand):
    cmd: Literal['download']
    remote_path: str
    local_path: str = '.'
    recurse: bool = False


class SliverSessionUPLOADCommand(SliverSessionCommand):
    cmd: Literal['upload']
    remote_path: str
    local_path: str = '.'
    recurse: bool = False
    is_ioc: bool = False


class SliverSessionNETSTATCommand(SliverSessionCommand):
    cmd: Literal['netstat']
    tcp: bool = True
    udp: bool = True
    ipv4: bool = True
    ipv6: bool = True
    listening: bool = True


class SliverSessionEXECCommand(SliverSessionCommand):
    cmd: Literal['execute']
    exe: str
    args: Optional[List[str]]
    output: bool = True


class SliverSessionSimpleCommand(SliverSessionCommand):
    cmd: Literal['ifconfig', 'ps', 'pwd']


class SliverSessionLSCommand(SliverSessionCommand):
    cmd: Literal['ls']
    remote_path: str


class SliverSessionPROCDUMPCommand(SliverSessionCommand):
    cmd: Literal['process_dump']
    local_path: str
    pid: str = Field(pattern=VAR_PATTERN)


class SliverSessionRMCommand(SliverSessionCommand):
    cmd: Literal['rm']
    remote_path: str
    recursive: bool = False
    force: bool = False


class SliverSessionTERMINATECommand(SliverSessionCommand):
    cmd: Literal['terminate']
    pid: str = Field(pattern=VAR_PATTERN)
    force: bool = False


class Config(BaseModel):
    sliver_config: SliverConfig = SliverConfig(config_file=None)
    msf_config: MsfConfig = MsfConfig(password=None)
    cmd_config: CommandConfig = CommandConfig(loop_sleep=5)


Commands = List[Union[
                         ShellCommand,
                         MsfModuleCommand,
                         MsfSessionCommand,
                         MsfPayloadCommand,
                         SleepCommand,
                         SSHCommand,
                         FatherCommand,
                         SFTPCommand,
                         DebugCommand,
                         SetVarCommand,
                         RegExCommand,
                         TempfileCommand,
                         IncludeCommand,
                         WebServCommand,
                         HttpClientCommand,
                         SliverSessionCDCommand,
                         SliverSessionLSCommand,
                         SliverSessionNETSTATCommand,
                         SliverSessionEXECCommand,
                         SliverSessionMKDIRCommand,
                         SliverSessionSimpleCommand,
                         SliverSessionDOWNLOADCommand,
                         SliverSessionUPLOADCommand,
                         SliverSessionPROCDUMPCommand,
                         SliverSessionRMCommand,
                         SliverSessionTERMINATECommand,
                         SliverHttpsListenerCommand,
                         SliverGenerateCommand
                         ]]


class Playbook(BaseModel):
    vars: Optional[Dict[str, str]] = None
    commands: Commands
