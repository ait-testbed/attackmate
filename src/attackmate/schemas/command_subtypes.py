from __future__ import annotations
from typing import Annotated, TypeAlias, Union
from pydantic import Field
# Core Commands
from .sleep import SleepCommand
from .shell import ShellCommand
from .setvar import SetVarCommand
from .include import IncludeCommand
from .loop import LoopCommand
from .http import WebServCommand, HttpClientCommand
from .father import FatherCommand
from .tempfile import TempfileCommand
from .debug import DebugCommand
from .regex import RegExCommand
from .vnc import VncCommand
from .json import JsonCommand
from .browser import BrowserCommand
from .ssh import SSHCommand, SFTPCommand
# Bettercap Commands
from .bettercap import BettercapCommand
# Metasploit Commands
from .metasploit import MsfModuleCommand, MsfSessionCommand, MsfPayloadCommand
# Sliver Commands
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

SliverSessionCommands: TypeAlias = Annotated[Union[
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
    SliverSessionTERMINATECommand], Field(discriminator='cmd')]


SliverCommands: TypeAlias = Annotated[Union[
    SliverHttpsListenerCommand,
    SliverGenerateCommand], Field(discriminator='cmd')]


# This excludes the AttackMateRemoteCommand type
RemotelyExecutableCommand: TypeAlias = Annotated[
    Union[
        SliverSessionCommands,
        SliverCommands,
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
        LoopCommand,
        WebServCommand,
        HttpClientCommand,
        JsonCommand,
        VncCommand,
        BettercapCommand,
    ],
    Field(discriminator='type'),
]
