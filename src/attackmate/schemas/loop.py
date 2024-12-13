from attackmate.schemas.base import BaseCommand
from pydantic import field_validator
from typing import Literal
from attackmate.command import CommandRegistry
from attackmate.schemas.playbook import Commands


@CommandRegistry.register('loop')
class LoopCommand(BaseCommand):
    @field_validator('background')
    @classmethod
    def bg_not_implemented_yet(cls, v):
        raise ValueError('background mode is unsupported for this command')

    type: Literal['loop']
    cmd: str = 'loop condition'
    commands: Commands
