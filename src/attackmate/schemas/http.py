from typing import Literal, Optional, Dict, Any
from .base import BaseCommand, StringNumber
from attackmate.command import CommandRegistry


@CommandRegistry.register('webserv')
class WebServCommand(BaseCommand):
    type: Literal['webserv']
    cmd: str = 'HTTP-GET'
    local_path: str
    port: StringNumber = '8000'
    address: str = '0.0.0.0'  # nosec
    keep_serving: bool = False


@CommandRegistry.register('http-client')
class HttpClientCommand(BaseCommand):
    type: Literal['http-client']
    cmd: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'] = 'GET'
    url: str
    output_headers: bool = False
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    local_path: Optional[str] = None
    useragent: str = 'AttackMate'
    follow: bool = False
    verify: bool = False
    http2: bool = False
