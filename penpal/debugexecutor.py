"""
debugexecutor.py
============================================
This class allows to print out variables.
"""

from .baseexecutor import BaseExecutor, Result
from .schemas import BaseCommand, DebugCommand


class DebugExecutor(BaseExecutor):

    def log_command(self, command: DebugCommand):
        self.logger.warn(f"Debug: '{command.cmd}'")
        if command.varstore:
            self.logger.warn(self.varstore.variables)

    def _exec_cmd(self, command: BaseCommand) -> Result:
        return Result("", 0)
