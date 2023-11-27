from typing import Literal
from .base import BaseCommand


class RegExCommand(BaseCommand):
    type: Literal['regex']
    mode: Literal['search', 'split', 'findall'] = 'findall'
    input: str = 'RESULT_STDOUT'
    output: dict[str, str]
