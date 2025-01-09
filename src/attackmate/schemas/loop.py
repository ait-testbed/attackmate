from attackmate.schemas.base import BaseCommand
from pydantic import field_validator
from typing import Literal, Union, Optional, List
from .sleep import SleepCommand
from .shell import ShellCommand
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


Commands = List[
    Union[
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
]


class LoopCommand(BaseCommand):
    @field_validator('background')
    @classmethod
    def bg_not_implemented_yet(cls, v):
        raise ValueError('background mode is unsupported for this command')

    type: Literal['loop']
    cmd: str = 'loop condition'
    commands: Commands
    break_if: Optional[str] = None
