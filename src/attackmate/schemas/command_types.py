

from typing import List, Annotated, TypeAlias, Union
from pydantic import Field
from attackmate.schemas.command_subtypes import RemotelyExecutableCommand
from attackmate.schemas.remote import AttackMateRemoteCommand


Command: TypeAlias = Union[
    RemotelyExecutableCommand,
    AttackMateRemoteCommand
]


Commands: TypeAlias = List[Command]]
