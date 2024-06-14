from typing import Literal, Optional
from pydantic import ValidationInfo, field_validator
from .base import BaseCommand
from pprint import pprint


class RegExCommand(BaseCommand):
    @field_validator('mode')
    @classmethod
    def sub_needs_replace(cls, v, info: ValidationInfo) -> str:
        if 'replace' in info.data and info.data['replace']:
            return v
        else:
            print(info.data)
            pprint(info)
            raise ValueError('Regex: sub needs the replace-setting!')

    type: Literal['regex']
    # replace is a dependency for mode, therefor it must be place BEFORE mode!
    replace: Optional[str] = None
    mode: Literal['search', 'split', 'findall', 'sub'] = 'findall'
    input: str = 'RESULT_STDOUT'
    output: dict[str, str]
