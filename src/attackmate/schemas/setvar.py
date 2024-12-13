from typing import Literal, Optional
from attackmate.schemas.base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('setvar')
class SetVarCommand(BaseCommand):
    type: Literal['setvar']
    variable: str
    encoder: Optional[str] = None
