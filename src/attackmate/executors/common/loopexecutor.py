"""
loopexecutor.py
============================================
Execute commands in a loop
"""

import copy
from typing import Callable
from string import Template
from attackmate.executors.baseexecutor import BaseExecutor
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

    def loop_range(self, command: LoopCommand, start: int, end: int) -> None:
        for x in range(start, end):
            for cmd in command.commands:
                template_cmd: Command = copy.deepcopy(cmd)
                tpl = Template(template_cmd.cmd)
                template_cmd.cmd = tpl.substitute(LOOP_INDEX=x, **self.varstore.variables)
                self.runfunc([template_cmd])

    def loop_items(self, command: LoopCommand, varname: str, iterable: list[str]) -> None:
        for x in iterable:
            for cmd in command.commands:
                template_cmd: Command = copy.deepcopy(cmd)
                tpl = Template(template_cmd.cmd)
                template_cmd.cmd = tpl.substitute(LOOP_ITEM=x, **self.varstore.variables)
                self.runfunc([template_cmd])

    def execute_loop(self, command: LoopCommand) -> None:
        m = re.search(r'range\(\s*(\d+)\s*,\s*(\d+)\s*\)', command.cmd)
        if m:
            range_start: int = int(m.group(1))
            range_end: int = int(m.group(2))
            if range_start > range_end:
                raise ExecException('range_start is bigger than range_end')
            else:
                return self.loop_range(command, range_start, range_end)

        m = re.search(r'items\(\s*([^\)]+)\s*\)', command.cmd)
        if m:
            var_name = m.group(1)
            listvar = self.varstore.get_list(var_name)
            if listvar:
                return self.loop_items(command, var_name, listvar)
            else:
                raise ExecException('list-variable does not exist')
        else:
            print('No valid condition found')

    def _exec_cmd(self, command: LoopCommand) -> Result:
        # idea: use runfunc with one command only
        # in that way it is possible to replace context-variables first
        # runfunc will replace global variables then
        self.execute_loop(command)
        self.logger.info('Loop ends')
        return Result('', 0)
