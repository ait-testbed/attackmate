"""
regexexecutor.py
============================================
This class allows to parse variables using
regular expressions.
"""

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.regex import RegExCommand
from string import Template
from typing import Match
import re
from attackmate.executors.executor_factory import executor_factory


@executor_factory.register_executor('regex')
class RegExExecutor(BaseExecutor):

    def log_command(self, command: RegExCommand):
        self.logger.warning(f"RegEx: '{command.cmd}', Mode: '{command.mode}'")

    def forge_variables(self, data, variable_name='MATCH'):
        result = {}
        if data is None:
            return None
        if isinstance(data, str):
            result[f'{variable_name}_0'] = data
        elif isinstance(data, (list, tuple)):
            for i, item in enumerate(data):
                tmpvar = f'{variable_name}_{str(i)}'
                if isinstance(item, str):
                    result[tmpvar] = item
                elif isinstance(item, (list, tuple)):
                    for j, level2 in enumerate(item):
                        tmpvar2 = f'{tmpvar}_{str(j)}'
                        if isinstance(level2, str):
                            result[tmpvar2] = level2

        return result

    def register_outputvars(self, outputvars: dict, matches):
        if not matches:
            self.logger.debug('no match!')
            self.varstore.set_variable('REGEX_MATCHES_LIST', [])
            return

        for k, v in outputvars.items():
            temp = Template(v)
            # register individual matches
            self.varstore.set_variable(k, temp.safe_substitute(matches))
            # extract all matches into a list
            matches_list = list(matches.values()) if isinstance(matches, dict) else []
            self.varstore.set_variable('REGEX_MATCHES_LIST', matches_list)

    def forge_and_register_variables(self, output: dict, data):
        matches = self.forge_variables(data)
        self.logger.debug(matches)
        self.register_outputvars(output, matches)
        return

    def _exec_cmd(self, command: RegExCommand) -> Result:
        self.setoutputvars = False
        if command.mode == 'findall':
            m = re.findall(command.cmd, self.varstore.get_str(command.input))
            self.forge_and_register_variables(command.output, m)
        if command.mode == 'split':
            m = re.split(command.cmd, self.varstore.get_str(command.input))
            self.forge_and_register_variables(command.output, m)
        if command.mode == 'search':
            # search() module will only return the first occurrence that matches the specified pattern.
            m3 = re.search(command.cmd, self.varstore.get_str(command.input))
            if m3 is not None and isinstance(m3, Match):
                self.forge_and_register_variables(command.output, m3.group())
            else:
                self.varstore.set_variable('REGEX_MATCHES_LIST', [])
        if command.mode == 'sub':
            if command.replace:
                replaced = re.sub(command.cmd, command.replace, self.varstore.get_str(command.input))
                self.forge_and_register_variables(command.output, replaced)

        return Result('', 0)
