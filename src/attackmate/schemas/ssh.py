from typing import Optional, Literal, List
from pydantic import ValidationInfo, field_validator
from .base import BaseCommand, StringNumber
from attackmate.command import CommandRegistry


class SSHBase(BaseCommand):
    @field_validator('session', 'creates_session')
    @classmethod
    def session_and_background_unsupported(cls, v, info: ValidationInfo) -> str:
        if 'background' in info.data and info.data['background']:
            raise ValueError('background mode combined with session is unsupported for SSH')
        return v

    hostname: Optional[str] = None
    port: StringNumber = None
    username: Optional[str] = None
    password: Optional[str] = None
    passphrase: Optional[str] = None
    key_filename: Optional[str] = None
    creates_session: Optional[str] = None
    session: Optional[str] = None
    clear_cache: bool = False
    timeout: float = 60
    jmp_hostname: Optional[str] = None
    jmp_port: StringNumber = None
    jmp_username: Optional[str] = None


@CommandRegistry.register('ssh')
class SSHCommand(SSHBase):
    type: Literal['ssh']
    interactive: bool = False
    command_timeout: StringNumber = '15'
    prompts: List[str] = ['$ ', '# ', '> ']
    bin: bool = False


@CommandRegistry.register('sftp')
class SFTPCommand(SSHBase):
    type: Literal['sftp']
    cmd: Literal['get', 'put']
    remote_path: str
    local_path: str
    mode: Optional[str] = None
