from attackmate.schemas.base import BaseCommand
from pydantic import field_validator
from typing import Literal


class IncludeCommand(BaseCommand):
    @field_validator('background')
    @classmethod
    def bg_not_implemented_yet(cls, v):
        raise ValueError('background mode is unsupported for this command')

    type: Literal['include']
    local_path: str
    cmd: str = 'include commands'
