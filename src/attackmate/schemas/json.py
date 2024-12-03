from typing import Literal, Optional
from .base import BaseCommand


class JsonCommand(BaseCommand):
    type: Literal['json']
    cmd: str
    varstore: Optional[bool] = False
