from typing import Literal
from pydantic import computed_field
from functools import cached_property
from random import randint
from attackmate.schemas.base import BaseCommand, StringNumber
from attackmate.command import CommandRegistry


@CommandRegistry.register('sleep')
class SleepCommand(BaseCommand):
    type: Literal['sleep']
    min_sec: StringNumber = '0'
    seconds: StringNumber = '1'
    random: bool = False
    cmd: str = 'sleep'

    @computed_field  # type: ignore[misc]
    @cached_property
    # calculates the actual sleep time based on whether random is enabled
    def sleep_time(self) -> int:
        if not self.random:
            return int(self.seconds)
        return randint(int(self.min_sec), int(self.seconds))
