import time
from random import randint
from .baseexecutor import BaseExecutor, Result


class SleepExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None):
        super().__init__(cmdconfig)
        self.sleep_time = None

    def set_sleeptime(self, command):
        if self.sleep_time is None:
            self.sleep_time = command.seconds
            if command.random:
                self.sleep_time = randint(command.min_sec, command.seconds)

    def log_command(self, command):
        self.set_sleeptime(command)
        self.logger.info(f"Sleeping {self.sleep_time} seconds")

    def _exec_cmd(self, command):
        self.set_sleeptime(command)
        time.sleep(self.sleep_time)
        return Result("Awake O_O", 0)
