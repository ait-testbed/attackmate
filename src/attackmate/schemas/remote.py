from __future__ import annotations
from pydantic import model_validator
from typing import Literal, Optional

from .base import BaseCommand
from attackmate.command import CommandRegistry

from .command_subtypes import RemotelyExecutableCommand


@CommandRegistry.register('remote')
class AttackMateRemoteCommand(BaseCommand):

    type: Literal['remote']
    cmd: Literal['execute_command', 'execute_playbook']
    server_url: str
    cacert: str  # TODO configure this file path in some configs elsewhere?
    user: str
    password: str
    playbook_yaml_content: Optional[str] = None
    playbook_file_path: Optional[str] = None
    remote_command: Optional[RemotelyExecutableCommand] = None

    # Common command parameters (like background, only_if) from BaseCommand
    # will be applied to the command itself, not the remote_command executed on the remote instance

    @model_validator(mode='after')
    def check_remote_command(self) -> 'AttackMateRemoteCommand':
        if self.cmd == 'execute_command' and not self.remote_command:
            raise ValueError("remote_command must be provided when cmd is 'execute_command'")
        if self.cmd == 'execute_playbook' and not self.playbook_yaml_content:
            raise ValueError("playbook_yaml_content must be provided when cmd is 'execute_playbook_yaml'")
        return self
