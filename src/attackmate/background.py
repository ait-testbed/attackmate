from .schemas import BaseCommand
from .processmanager import ProcessManager
from .result import Result
from typing import Any
import logging


class Background:
    def __getstate__(self):
        """
        pm contains the states of the processes.
        This environment must not be in the subprocess!
        """
        state = self.__dict__.copy()
        state['pm'] = None
        return state

    def __init__(self, pm: ProcessManager):
        self.logger = logging.getLogger('playbook')
        self.pm = pm

    def exec_background(self, command: BaseCommand):
        if hasattr(command, "type"):
            self.logger.info(f"Run in background: {command.type}({command.cmd})")
        else:
            self.logger.info(f"Run in background: {command.cmd}")
        p = self.pm.ctx.Process(target=self.exec,
                                args=(command,))
        p.start()
        self.pm.add_process(p, command.kill_on_exit)

    def _exec_cmd(self, command: Any) -> Result:
        return Result(None, None)

    def exec(self, command: BaseCommand):
        self._exec_cmd(command)
