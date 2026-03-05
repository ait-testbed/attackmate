from typing import Optional, Literal
from .base import BaseCommand, StringNumber
from pydantic import model_validator
from attackmate.command import CommandRegistry


@CommandRegistry.register('vnc')
class VncCommand(BaseCommand):

    type: Literal['vnc']
    cmd: Literal['key', 'type', 'move', 'capture', 'click', 'rightclick', 'expectscreen', 'close']
    hostname: Optional[str] = None
    port: Optional[StringNumber] = None
    display: Optional[StringNumber] = None
    password: Optional[str] = None
    key: Optional[str] = None
    input: Optional[str] = None
    filename: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    creates_session: Optional[str] = None
    session: Optional[str] = None
    maxrms: Optional[float] = 0
    expect_timeout: Optional[int] = 60
    connection_timeout: Optional[int] = 60

    @model_validator(mode='after')
    def check_cmd_requirements(self) -> 'VncCommand':
        cmd = self.cmd

        if self.background:
            raise ValueError('background mode is unsupported for VNC')
        if self.creates_session is not None and self.session is not None:
            raise ValueError('Cannot specify both "creates_session" and "session" at the same time.')

        required_fields = {
            'type': ['input'],
            'key': ['key'],
            'capture': ['filename'],
            'expectscreen': ['filename'],
            'move': ['x', 'y'],
        }

        if cmd in required_fields:
            missing_fields = [field for field in required_fields[cmd] if getattr(self, field, None) is None]
            if missing_fields:
                raise ValueError(f'Command "{cmd}" requires {", ".join(missing_fields)} field(s).')

        return self
