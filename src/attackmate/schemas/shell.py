from typing import Literal
from attackmate.schemas.base import BaseCommand


class ShellCommand(BaseCommand):
    type: Literal['shell']
