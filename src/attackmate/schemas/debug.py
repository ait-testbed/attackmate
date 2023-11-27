from typing import Literal
from .base import BaseCommand


class DebugCommand(BaseCommand):
    type: Literal['debug']
    varstore: bool = False
    exit: bool = False
    cmd: str = ''
