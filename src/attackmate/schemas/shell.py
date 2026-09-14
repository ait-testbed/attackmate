from typing import List, Literal, Optional
from pydantic import ValidationInfo, field_validator, model_validator
from attackmate.schemas.base import StringNumber
from attackmate.schemas.base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('shell')
class ShellCommand(BaseCommand):
    @field_validator('session', 'creates_session')
    @classmethod
    def session_and_background_unsupported(cls, v, info: ValidationInfo) -> str:
        if 'background' in info.data and info.data['background']:
            raise ValueError('background mode combined with session is unsupported for SSH')
        return v

    @model_validator(mode='after')
    def wait_for_exit_needs_text(self) -> 'ShellCommand':
        """``wait_for_exit`` appends a marker, which raw bytes cannot carry."""
        if self.wait_for_exit and self.bin:
            raise ValueError('wait_for_exit cannot be combined with bin mode')
        return self

    @model_validator(mode='after')
    def default_expand_keys_to_pty(self) -> 'ShellCommand':
        """Turn key expansion on by default for pty commands only.

        Driving a terminal application means sending keystrokes, so ``<ESC>``
        and friends are what a pty user wants. Existing non-pty playbooks must
        keep sending their text verbatim, and anyone who really wants a literal
        ``<ESC>`` under pty can still say ``expand_keys: False`` - checking
        ``model_fields_set`` distinguishes an explicit False from the default.
        """
        if self.pty and 'expand_keys' not in self.model_fields_set:
            self.expand_keys = True
        return self

    type: Literal['shell']
    interactive: bool = False
    creates_session: Optional[str] = None
    session: Optional[str] = None
    command_timeout: StringNumber = '10'
    read: bool = True
    command_shell: str = '/bin/sh'
    bin: Optional[bool] = False
    pty: bool = False
    raw: bool = True
    screen: bool = False
    expand_keys: bool = False
    term: str = 'xterm-256color'
    pty_rows: StringNumber = '24'
    pty_cols: StringNumber = '80'
    prompts: List[str] = []
    read_timeout: StringNumber = None
    wait_for_exit: bool = False
