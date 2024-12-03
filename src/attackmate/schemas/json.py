from typing import Literal, Optional
from .base import BaseCommand


class JsonCommand(BaseCommand):
    type: Literal['json']
    file: str
    varstore: Optional[bool]
