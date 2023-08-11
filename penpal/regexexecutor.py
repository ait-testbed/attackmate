"""
regexexecutor.py
============================================
This class allows to parse variables using 
regular expressions.
"""

from .baseexecutor import BaseExecutor, Result
from .schemas import BaseCommand, RegExCommand
import re


class RegExExecutor(BaseExecutor):

    def log_command(self, command: RegExCommand):
        self.logger.warn(f"RegEx: '{command.cmd}'")

    def _exec_cmd(self, command: RegExCommand) -> Result:
        if command.mode == 'findall':
            m = re.findall(command.cmd, self.varstore.get_variable(command.input))
            self.logger.debug(m)
        if command.mode == 'split':
            m = re.split(command.cmd, self.varstore.get_variable(command.input))
            self.logger.debug(m)
        if command.mode == 'search':
            m = re.search(command.cmd, self.varstore.get_variable(command.input))
            self.logger.debug(m.groups())
            

        return Result("", 0)
