from typing import List, Annotated, TypeAlias, Union
from pydantic import Field

from attackmate.schemas.command_subtypes import RemotelyExecutableCommand
from attackmate.schemas.remote import AttackMateRemoteCommand
from pydantic import Field


Command: TypeAlias = Annotated[Union[
    RemotelyExecutableCommand,
    AttackMateRemoteCommand
], Field(discriminator='type')]



Commands:  TypeAlias = List[Command]
