from typing import List, Literal, Union, Optional, Dict
from pydantic import BaseModel

# https://stackoverflow.com/questions/71539448/using-different-pydantic-models-depending-on-the-value-of-fields


class BaseCommand(BaseModel):
    error_if: Optional[str] = None
    error_if_not: Optional[str] = None
    loop_if: Optional[str] = None
    loop_if_not: Optional[str] = None
    loop_count: int = 3
    cmd: str


class SleepCommand(BaseCommand):
    type: Literal['sleep']
    min_sec: int = 0
    seconds: int = 1
    random: bool = False
    cmd: str = "sleep"


class ShellCommand(BaseCommand):
    type: Literal['shell']


class SSHCommand(BaseCommand):
    type: Literal['ssh']
    hostname: Optional[str]
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]
    passphrase: Optional[str]
    key_filename: Optional[str]
    timeout: float = 60


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


class MsfConfig(BaseModel):
    password: Optional[str] = None
    ssl: bool = True
    port: int = 55553
    server: Optional[str] = "127.0.0.1"
    uri: Optional[str] = "/api/"


class Config(BaseModel):
    msf_config: MsfConfig = MsfConfig(password=None)
    cmd_config: CommandConfig = CommandConfig(loop_sleep=5)
    vars: Optional[Dict[str, str]] = None
    commands: List[Union[ShellCommand, MsfModuleCommand, MsfSessionCommand, SleepCommand, SSHCommand]]
