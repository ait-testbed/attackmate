from typing import Literal, Optional
from pydantic import ValidationInfo, field_validator
from attackmate.schemas.base import StringNumber
from attackmate.schemas.base import BaseCommand


class ShellCommand(BaseCommand):
    @field_validator('session', 'creates_session')
    @classmethod
    def session_and_background_unsupported(cls, v, info: ValidationInfo) -> str:
        if 'background' in info.data and info.data['background']:
            raise ValueError('background mode combined with session is unsupported for SSH')
        return v

    type: Literal['shell']
    interactive: bool = False
    creates_session: Optional[str] = None
    session: Optional[str] = None
    command_timeout: StringNumber = '10'
    read: bool = True
    command_shell: str = '/bin/sh'
