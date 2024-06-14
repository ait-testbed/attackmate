from typing import List, Union, Optional, Dict
from pydantic import BaseModel
from .sleep import SleepCommand
from .shell import ShellCommand
from .setvar import SetVarCommand
from .include import IncludeCommand
from .metasploit import (MsfModuleCommand,
                         MsfSessionCommand,
                         MsfPayloadCommand)

from .sliver import (SliverSessionCDCommand,
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
                     SliverGenerateCommand)
from .ssh import SSHCommand, SFTPCommand
from .http import WebServCommand, HttpClientCommand
from .father import FatherCommand
from .tempfile import TempfileCommand
from .debug import DebugCommand
from .regex import RegExCommand
from .base import StrInt


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
    vars: Optional[Dict[str, StrInt]] = None
    commands: Commands
