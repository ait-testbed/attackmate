from typing import Literal, Optional
from pydantic import field_validator, ValidationInfo
from .base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('json')
class JsonCommand(BaseCommand):
    type: Literal['json']
    cmd: str = 'no/valid/path'
    local_path: Optional[str] = None
    varstore: Optional[bool] = False

    @field_validator('cmd', mode='after')
    @classmethod
    def validate_cmd_or_local_path(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        # Check if both cmd and local_path are missing
        if v == 'no/valid/path' and not info.data.get('local_path'):
            raise ValueError("At least one of 'cmd' or 'local_path' must be set in JsonCommand.")
        return v
