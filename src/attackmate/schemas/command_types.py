

from typing import List, TypeAlias, Union
from attackmate.schemas.command_subtypes import RemotelyExecutableCommand
from attackmate.schemas.remote import AttackMateRemoteCommand


Command: TypeAlias = Union[
    RemotelyExecutableCommand,
    AttackMateRemoteCommand
]


Commands: TypeAlias = List[Command]
