"""
debugexecutor.py
============================================
This class allows to print out variables.
"""

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.debug import DebugCommand


class DebugExecutor(BaseExecutor):

    def log_command(self, command: DebugCommand):
        self.logger.warn(f"Debug: '{command.cmd}'")
        if command.varstore:
            self.logger.warn(self.varstore.variables)

    def _exec_cmd(self, command: DebugCommand) -> Result:
        self.setoutuptvars = False
        ret = 0
        if command.exit:
            ret = 1

        return Result('', ret)
