from typing import Literal, Optional
from pydantic import ValidationInfo, field_validator
from .base import BaseCommand
from pprint import pprint
import logging

logger = logging.getLogger('playbook')


class RegExCommand(BaseCommand):

    @field_validator('mode')
    @classmethod
    def sub_needs_replace(cls, v, info: ValidationInfo) -> str:

        if v == 'sub' and not info.data.get('replace'):
            print(info.data)
            pprint(info)
            logger.error('Error parsing playbook. command mode: sub must be preceded by replace setting!')
            raise ValueError('Regex sub mode needs replace-setting!')

        return v

    type: Literal['regex']
    # replace is a dependency for mode, therefore it must be placed BEFORE mode!
    replace: Optional[str] = None
    mode: Literal['search', 'split', 'findall', 'sub'] = 'findall'
    input: str = 'RESULT_STDOUT'
    output: dict[str, str]
