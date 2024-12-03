"""
loopexecutor.py
============================================
Execute commands in a loop
"""

import copy
from typing import Callable
from string import Template
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.executors.features.conditional import Conditional
from attackmate.result import Result
from attackmate.schemas.loop import LoopCommand
from attackmate.schemas.playbook import Commands, Command
from attackmate.variablestore import VariableStore
from attackmate.execexception import ExecException
from attackmate.processmanager import ProcessManager
from attackmate.executors.executor_factory import executor_factory
import re


@executor_factory.register_executor('loop')
class LoopExecutor(BaseExecutor):
    def __init__(
        self,
        pm: ProcessManager,
        cmdconfig=None,
        *,
        varstore: VariableStore,
        runfunc: Callable[[Commands], None],
    ):
        self.runfunc = runfunc
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: LoopCommand):
        self.logger.info('Looping commands')

    def break_condition_met(self, command: LoopCommand) -> bool:
        if not command.break_condition:
            return False
        condition = Template(command.break_condition).safe_substitute(**self.varstore.variables)
        if Conditional.test(condition):
            self.logger.warning('Breaking out of loop due to condition: %s', command.break_condition)
            return True
        return False

    def loop_range(self, command: LoopCommand, start: int, end: int) -> None:
        for x in range(start, end):
            for cmd in command.commands:
                template_cmd: Command = copy.deepcopy(cmd)
                tpl = Template(template_cmd.cmd)
                template_cmd.cmd = tpl.substitute(LOOP_INDEX=x, **self.varstore.variables)
                if self.break_condition_met(command):
                    return
                self.runfunc([template_cmd])

    def loop_items(self, command: LoopCommand, varname: str, iterable: list[str]) -> None:
        for x in iterable:
            for cmd in command.commands:
                template_cmd: Command = copy.deepcopy(cmd)
                tpl = Template(template_cmd.cmd)
                template_cmd.cmd = tpl.substitute(LOOP_ITEM=x, **self.varstore.variables)
                if self.break_condition_met(command):
                    return
                self.runfunc([template_cmd])

    def execute_loop(self, command: LoopCommand) -> None:
        range_match = re.search(r'range\(\s*(\d+)\s*,\s*(\d+)\s*\)', command.cmd)
        if range_match:
            range_start, range_end = map(int, range_match.groups())
            if range_start > range_end:
                raise ExecException('range_start is bigger than range_end')
            self.loop_range(command, range_start, range_end)
            return

        items_match = re.search(r'items\(\s*([^\)]+)\s*\)', command.cmd)
        if items_match:
            var_name = items_match.group(1)
            listvar = self.varstore.get_list(var_name)
            if listvar is None:
                raise ExecException(f"List variable '{var_name}' does not exist")
            self.loop_items(command, var_name, listvar)
            return
        self.logger.warning('No valid loop condition found in command: %s', command.cmd)

    def _exec_cmd(self, command: LoopCommand) -> Result:
        # idea: use runfunc with one command only
        # in that way it is possible to replace context-variables first
        # runfunc will replace global variables then
        self.execute_loop(command)
        self.logger.info('Loop execution complete')
        return Result('', 0)
