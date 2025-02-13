from typing import Literal, Optional
from attackmate.schemas.base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('browser')
class BrowserCommand(BaseCommand):
    type: Literal['browser']
    cmd: Literal['visit', 'click', 'type', 'screenshot'] = 'visit'
    url: Optional[str] = None
    selector: Optional[str] = None
    text: Optional[str] = None
    screenshot_path: Optional[str] = None
    creates_session: Optional[str] = None
    session: Optional[str] = None
