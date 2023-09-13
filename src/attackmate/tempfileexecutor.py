"""
tempfileexecutor.py
============================================
Creates temporary files and directories
"""

import tempfile
from typing import Any
from .baseexecutor import BaseExecutor
from .result import Result
from .schemas import TempfileCommand
from .variablestore import VariableStore
from .processmanager import ProcessManager


class TempfileExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, varstore: VariableStore, cmdconfig=None):
        self.tempfilestore: dict[str, Any] = {}
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: TempfileCommand):
        if command.cmd == "dir":
            self.logger.warn("Creating temporary directory..")
        else:
            self.logger.warn("Creating temporary file..")

    def _exec_cmd(self, command: TempfileCommand) -> Result:
        ret = 0
        fullpath = ""
        if command.cmd == "dir":
            tmpfile = tempfile.TemporaryDirectory()
            self.tempfilestore[command.variable] = tmpfile
            fullpath = tmpfile.name
        else:
            tmpdir = tempfile.NamedTemporaryFile()
            self.tempfilestore[command.variable] = tmpdir
            fullpath = tmpdir.name

        self.varstore.set_variable(command.variable, fullpath)

        return Result(fullpath, ret)
