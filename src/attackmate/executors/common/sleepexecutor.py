import time
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.executors.executor_factory import executor_factory


@executor_factory.register_executor('sleep')
class SleepExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *, varstore: VariableStore):
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command):
        self.logger.info(f'Sleeping {command.sleep_time} seconds')

    def _exec_cmd(self, command):
        time.sleep(command.sleep_time)
        return Result('Awake O_O', 0)
