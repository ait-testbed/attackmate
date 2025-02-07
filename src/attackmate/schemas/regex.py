from typing import Literal, Optional
from pydantic import ValidationInfo, field_validator
from .base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('regex')
class RegExCommand(BaseCommand):

    @field_validator('mode')
    @classmethod
    def sub_needs_replace(cls, v, info: ValidationInfo) -> str:

        if v == 'sub' and not info.data.get('replace'):
            raise ValueError(
                'Error parsing playbook. regex command mode: sub must be preceded by replace setting!'
            )

        return v

    type: Literal['regex']
    # replace is a dependency for mode, therefore it must be placed BEFORE mode!
    replace: Optional[str] = None
    mode: Literal['search', 'split', 'findall', 'sub'] = 'findall'
    input: str = 'RESULT_STDOUT'
    output: dict[str, str]
