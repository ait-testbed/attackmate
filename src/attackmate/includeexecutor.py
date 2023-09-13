"""
includeexecutor.py
============================================
Execute commands from a yaml-file
"""

import yaml
from typing import Callable
from .baseexecutor import BaseExecutor
from .result import Result
from .schemas import IncludeCommand, Playbook, Commands
from .variablestore import VariableStore
from .execexception import ExecException
from .processmanager import ProcessManager


class IncludeExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *,
                 varstore: VariableStore,
                 runfunc: Callable[[Commands], None]):
        self.runfunc = runfunc
        super().__init__(pm, varstore, cmdconfig)

    def load_file(self, local_path: str) -> Playbook:
        try:
            with open(local_path) as f:
                config = yaml.safe_load(f)
                return Playbook.parse_obj(config)
        except Exception as e:
            raise ExecException(e)

    def log_command(self, command: IncludeCommand):
        self.logger.info(f"Executing commands from '{command.local_path}'")

    def _exec_cmd(self, command: IncludeCommand) -> Result:
        playbook = self.load_file(command.local_path)
        self.runfunc(playbook.commands)
        return Result("", 0)
