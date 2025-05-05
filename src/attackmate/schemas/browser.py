from pydantic import model_validator
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
    headless: Optional[bool] = None

    @model_validator(mode='after')
    def validate_browser_command(self) -> 'BrowserCommand':
        if self.background:
            raise ValueError('background mode is unsupported for browser commands')

        if self.cmd == 'visit':
            if not self.url:
                raise ValueError("`visit` command requires a 'url'")
        elif self.cmd == 'type':
            if not self.selector or not self.text:
                raise ValueError("`type` command requires both 'selector' and 'text'")
        elif self.cmd == 'click':
            if not self.selector:
                raise ValueError("`click` command requires 'selector'")
        return self
