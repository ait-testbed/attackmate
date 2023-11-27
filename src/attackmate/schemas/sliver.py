from typing import Literal, Optional, List
from .base import BaseCommand, StringNumber


class SliverHttpsListenerCommand(BaseCommand):
    type: Literal['sliver']
    cmd: Literal['start_https_listener']
    host: str = '0.0.0.0'  # nosec
    port: StringNumber = '443'
    domain: str = ''
    website: str = ''
    acme: bool = False
    persistent: bool = False
    enforce_otp: bool = True
    randomize_jarm: bool = True
    long_poll_timeout: StringNumber = '1'
    long_poll_jitter: StringNumber = '3'
    timeout: StringNumber = '60'


class SliverGenerateCommand(BaseCommand):
    type: Literal['sliver']
    cmd: Literal['generate_implant']
    target: Literal[
            'darwin/amd64',
            'darwin/arm64',
            'linux/386',
            'linux/amd64',
            'windows/386',
            'windows/amd64'] = 'linux/amd64'
    c2url: str
    format: Literal[
            'EXECUTABLE',
            'SERVICE',
            'SHARED_LIB',
            'SHELLCODE'] = 'EXECUTABLE'
    name: str
    filepath: Optional[str] = None
    IsBeacon: bool = False
    BeaconInterval: StringNumber = '120'
    RunAtLoad: bool = False
    Evasion: bool = False


class SliverSessionCommand(BaseCommand):
    type: Literal['sliver-session']
    session: str
    beacon: bool = False


class SliverSessionCDCommand(SliverSessionCommand):
    cmd: Literal['cd']
    remote_path: str


class SliverSessionMKDIRCommand(SliverSessionCommand):
    cmd: Literal['mkdir']
    remote_path: str


class SliverSessionDOWNLOADCommand(SliverSessionCommand):
    cmd: Literal['download']
    remote_path: str
    local_path: str = '.'
    recurse: bool = False


class SliverSessionUPLOADCommand(SliverSessionCommand):
    cmd: Literal['upload']
    remote_path: str
    local_path: str = '.'
    recurse: bool = False
    is_ioc: bool = False


class SliverSessionNETSTATCommand(SliverSessionCommand):
    cmd: Literal['netstat']
    tcp: bool = True
    udp: bool = True
    ipv4: bool = True
    ipv6: bool = True
    listening: bool = True


class SliverSessionEXECCommand(SliverSessionCommand):
    cmd: Literal['execute']
    exe: str
    args: Optional[List[str]] = None
    output: bool = True


class SliverSessionSimpleCommand(SliverSessionCommand):
    cmd: Literal['ifconfig', 'ps', 'pwd']


class SliverSessionLSCommand(SliverSessionCommand):
    cmd: Literal['ls']
    remote_path: str


class SliverSessionPROCDUMPCommand(SliverSessionCommand):
    cmd: Literal['process_dump']
    local_path: str
    pid: StringNumber


class SliverSessionRMCommand(SliverSessionCommand):
    cmd: Literal['rm']
    remote_path: str
    recursive: bool = False
    force: bool = False


class SliverSessionTERMINATECommand(SliverSessionCommand):
    cmd: Literal['terminate']
    pid: StringNumber
    force: bool = False
