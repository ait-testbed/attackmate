from typing import Literal
from attackmate.schemas.base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('session')
class SessionCommand(BaseCommand):
    """Close or inspect an open session from within a playbook.

    Sessions used to live until the end of the run with no way to close one
    early, and no way to ask whether one was still alive - so a playbook could
    only find out that its foothold had dropped by sending a command into it
    and failing.
    """

    type: Literal['session']
    cmd: Literal['close', 'status'] = 'close'
    session: str
    executor: Literal['shell', 'ssh'] = 'shell'
