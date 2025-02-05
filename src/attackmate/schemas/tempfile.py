from typing import Literal
from .base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('mktemp')
class TempfileCommand(BaseCommand):
    type: Literal['mktemp']
    cmd: Literal['file', 'dir'] = 'file'
    variable: str
