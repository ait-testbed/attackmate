"""
vncexecutor.py
============================================
This class enables executing commands via
vnc.
"""

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.schemas.vnc import VncCommand


class VncExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *, varstore: VariableStore):
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: VncCommand):
        self.logger.info(f"Executing Vnc-Command: '{command.cmd}. Port: {command.port}'")

    def _exec_cmd(self, command: VncCommand) -> Result:

        output = ''
        return Result(output, 0)
