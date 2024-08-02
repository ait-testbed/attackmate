from typing import Optional, Literal
from .base import BaseCommand, StringNumber


class VncCommand(BaseCommand):
    type: Literal['vnc']
    hostname: Optional[str] = None
    port: Optional[StringNumber] = 5900
