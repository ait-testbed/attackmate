from typing import Literal
from .base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('debug')
class DebugCommand(BaseCommand):
    type: Literal['debug']
    varstore: bool = False
    exit: bool = False
    cmd: str = ''
