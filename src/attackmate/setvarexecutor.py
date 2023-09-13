"""
setvarexecutor.py
============================================
This class allows to set variables.
"""

from .baseexecutor import BaseExecutor
from .result import Result
from .schemas import SetVarCommand


class SetVarExecutor(BaseExecutor):

    def log_command(self, command: SetVarCommand):
        self.logger.warn(f"Setting Variable: '{command.variable}'")

    def _exec_cmd(self, command: SetVarCommand) -> Result:
        self.varstore.set_variable(command.variable, command.cmd)

        return Result("", 0)
