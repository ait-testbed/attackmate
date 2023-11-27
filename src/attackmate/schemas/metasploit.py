from typing import Literal, Optional, Dict
from pydantic import field_validator
from .base import StringNumber
from attackmate.schemas.base import BaseCommand


class MsfSessionCommand(BaseCommand):
    @field_validator('background')
    @classmethod
    def bg_not_implemented_yet(cls, v):
        raise ValueError('background mode is unsupported for this command')

    type: Literal['msf-session']
    cmd: str
    stdapi: bool = False
    write: bool = False
    read: bool = False
    session: str
    end_str: Optional[str] = None


class MsfPayloadCommand(BaseCommand):
    type: Literal['msf-payload']
    cmd: str
    format: str = 'raw'
    badchars: str = ''
    force_encode: bool = False
    encoder: str = ''
    template: Optional[str] = None
    platform: Optional[str] = None
    keep_template_working: bool = False
    nopsled_size: StringNumber = '0'
    iter: StringNumber = '0'
    payload_options: Dict[str, str] = {}
    local_path: Optional[str] = None


class MsfModuleCommand(BaseCommand):
    cmd: str
    type: Literal['msf-module']
    target: StringNumber = '0'
    creates_session: Optional[str] = None
    session: Optional[str] = None
    payload: Optional[str] = None
    options: Dict[str, str] = {}
    payload_options: Dict[str, str] = {}

    def is_interactive(self):
        if self.interactive is not None:
            return self.interactive
        if self.module_type() == 'exploit':
            return True
        else:
            return False

    def module_type(self):
        if self.cmd is None:
            return None
        return self.cmd.split('/')[0]

    def module_path(self):
        if self.cmd is None:
            return None
        return '/'.join(self.cmd.split('/')[1:])
