from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from typing import Literal, Optional, Dict, Any, List, Union, TypeAlias

from .base import BaseCommand
from attackmate.command import CommandRegistry

from .sleep import SleepCommand
from .shell import ShellCommand
from .vnc import VncCommand
from .setvar import SetVarCommand
from .include import IncludeCommand
from .metasploit import MsfModuleCommand, MsfSessionCommand, MsfPayloadCommand

from .sliver import (
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
    SliverGenerateCommand,
)
from .ssh import SSHCommand, SFTPCommand
from .http import WebServCommand, HttpClientCommand
from .father import FatherCommand
from .tempfile import TempfileCommand
from .debug import DebugCommand
from .regex import RegExCommand
from .browser import BrowserCommand


RemoteCommand: TypeAlias = Union[
    BrowserCommand,
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
    VncCommand,
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
    SliverGenerateCommand,
]


@CommandRegistry.register('remote')
class AttackMateRemoteCommand(BaseCommand):

    type: Literal['remote']
    cmd: Literal['execute_command', 'execute_playbook_yaml', 'execute_playbook_file']
    server_url: str
    cacert: str  # configure this file path in some configs elsewhere?
    user: str
    password: str
    playbook_yaml_content: Optional[str] = None
    playbook_file_path: Optional[str] = None
    remote_command: Optional[RemoteCommand] = None

    # Common command parameters (like background, only_if) from BaseCommand
    # will be applied to the 'remote' command itself, not the remote_command directly -> note in docs

    @model_validator(mode='after')
    def check_remote_command(self) -> 'AttackMateRemoteCommand':
        if self.cmd == 'execute_command' and not self.remote_command:
            raise ValueError("remote_command must be provided when cmd is 'execute_command'")
        if self.cmd == 'execute_playbook_yaml' and not self.playbook_yaml_content:
            raise ValueError("playbook_yaml_content must be provided when cmd is 'execute_playbook_yaml'")
        if self.cmd == 'execute_playbook_file' and not self.playbook_file_path:
            raise ValueError("playbook_file_path must be provided when cmd is 'execute_playbook_file'")
        return self
