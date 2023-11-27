from typing import Literal
from attackmate.schemas.base import BaseCommand, StringNumber


class SleepCommand(BaseCommand):
    type: Literal['sleep']
    min_sec: StringNumber = '0'
    seconds: StringNumber = '1'
    random: bool = False
    cmd: str = 'sleep'
