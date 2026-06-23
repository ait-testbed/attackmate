from pydantic import Field
from typing import List, TypeAlias, Union, Annotated
from attackmate.schemas.command_subtypes import RemotelyExecutableCommand
from attackmate.schemas.remote import AttackMateRemoteCommand


Command: TypeAlias = Annotated[Union[
    RemotelyExecutableCommand,
    AttackMateRemoteCommand
], Field(discriminator='type')]

Commands: TypeAlias = List[Command]
