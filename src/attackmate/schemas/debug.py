from typing import Literal
from .base import BaseCommand


class DebugCommand(BaseCommand):
    type: Literal['debug']
    varstore: bool = False
    exit: bool = False
    wait_for_key: bool = False
    cmd: str = ''
