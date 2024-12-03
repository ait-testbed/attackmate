"""
jsonexecutor.py
============================================
This class allows to load variables from a json file
"""

from attackmate.executors.baseexecutor import BaseExecutor

from attackmate.schemas.json import JsonCommand
from attackmate.result import Result
from attackmate.executors.executor_factory import executor_factory


@executor_factory.register_executor('json')
class DebugExecutor(BaseExecutor):

    def log_command(self, command: JsonCommand):
        self.logger.warning(f"Loading variables from json file: '{command.file}'")
        if command.varstore:
            self.logger.warning(self.varstore.variables)

    def _exec_cmd(self, command: JsonCommand) -> Result:
        return Result('', 0)
