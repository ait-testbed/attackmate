"""
regexexecutor.py
============================================
This class allows to parse variables using
regular expressions.
"""

from .baseexecutor import BaseExecutor, Result
from .schemas import RegExCommand
from string import Template
import re


class RegExExecutor(BaseExecutor):

    def forge_variables(self, data, variable_name="MATCH"):
        result = {}
        if data is None:
            return None
        if isinstance(data, str):
            result[variable_name] = data
        elif isinstance(data, list) or isinstance(data, tuple):
            i = 0
            for item in data:
                tmpvar = f"{variable_name}_{str(i)}"
                if isinstance(item, str):
                    result[tmpvar] = item
                elif isinstance(item, list) or isinstance(item, tuple):
                    j = 0
                    for level2 in item:
                        tmpvar2 = f"{tmpvar}_{str(j)}"
                        if isinstance(level2, str):
                            result[tmpvar2] = level2
                        j += 1
                i += 1
        return result

    def log_command(self, command: RegExCommand):
        self.logger.warn(f"RegEx: '{command.cmd}'")

    def register_outputvars(self, outputvars: dict, matches):
        for k, v in outputvars.items():
            temp = Template(v)
            self.varstore.set_variable(k, temp.safe_substitute(matches))

    def _exec_cmd(self, command: RegExCommand) -> Result:
        if command.mode == 'findall':
            m = re.findall(command.cmd, self.varstore.get_variable(command.input))
            matches = self.forge_variables(m)
            self.logger.debug(matches)
            self.register_outputvars(command.output, matches)
        if command.mode == 'split':
            m = re.split(command.cmd, self.varstore.get_variable(command.input))
            matches = self.forge_variables(m)
            self.logger.debug(matches)
            self.register_outputvars(command.output, matches)
        if command.mode == 'search':
            m = re.search(command.cmd, self.varstore.get_variable(command.input))
            matches = self.forge_variables(m.groups())
            self.logger.debug(matches)
            self.register_outputvars(command.output, matches)

        return Result("", 0)
