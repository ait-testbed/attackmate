"""
debugexecutor.py
============================================
This class allows to print out variables.
"""

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.debug import DebugCommand
from attackmate.executors.executor_factory import executor_factory


@executor_factory.register_executor('debug')
class DebugExecutor(BaseExecutor):

    def log_command(self, command: DebugCommand):
        self.logger.warning(f"Debug: '{command.cmd}'")
        if command.varstore:
            self.logger.warning(self.varstore.variables)

    def _exec_cmd(self, command: DebugCommand) -> Result:
        self.setoutputvars = False
        ret = 0
        if command.wait_for_key:
            self.logger.warning("Type enter to continue")
            input()
        if command.exit:
            ret = 1

        return Result(f"Debug: '{command.cmd}'", ret)
