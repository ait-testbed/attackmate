import time
from random import randint
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


class SleepExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *, varstore: VariableStore):
        super().__init__(pm, varstore, cmdconfig)
        self.sleep_time = None

    def set_sleeptime(self, command):
        self.sleep_time = CmdVars.variable_to_int('seconds', command.seconds)
        if command.random:
            self.sleep_time = randint(CmdVars.variable_to_int('min_sec', command.min_sec),  # nosec
                                      CmdVars.variable_to_int('seconds', command.seconds))  # nosec

    def log_command(self, command):
        self.set_sleeptime(command)
        self.logger.info(f'Sleeping {self.sleep_time} seconds')

    def _exec_cmd(self, command):
        time.sleep(self.sleep_time)
        return Result('Awake O_O', 0)
