from typing import Literal
from .base import BaseCommand


class TempfileCommand(BaseCommand):
    type: Literal['mktemp']
    cmd: Literal['file', 'dir'] = 'file'
    variable: str
