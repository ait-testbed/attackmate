from typing import Literal, Optional
from attackmate.schemas.base import BaseCommand


class SetVarCommand(BaseCommand):
    type: Literal['setvar']
    variable: str
    encoder: Optional[str] = None
