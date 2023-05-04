"""
shellexecutor.py
============================================
This class enables executing shell
commands in PenPal.
"""

import subprocess
from .baseexecutor import BaseExecutor, Result
from .schemas import BaseCommand


class ShellExecutor(BaseExecutor):

    def log_command(self, command: BaseCommand):
        self.logger.info(f"Executing Shell-Command: '{command.cmd}'")

    def _exec_cmd(self, command: BaseCommand) -> Result:
        result = subprocess.run(command.cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        return Result(result.stdout.decode(), result.returncode)
