import re
import time
import logging
from attackmate.cmdvars import CmdVars

from attackmate.exitonerror import ExitOnError
from .result import Result
from .execexception import ExecException
from .schemas import BaseCommand
from .conditional import Conditional
from .variablestore import VariableStore
from typing import Any


class BaseExecutor(ExitOnError, CmdVars):
    """

    The BaseExecutor is the base class of all Executors.
    It enables base functionality for all Executors and
    provides a structure for all Executors.

    In order to create a custom Executor, one must simply
    derive from the BaseExecutor and implement the method
    _exec_cmd()

    """
    def __init__(self, variablestore: VariableStore, cmdconfig=None):
        """ Constructor for BaseExecutor

        Parameters
        ----------
        cmdconfig : str, default `None`
            cmd_config settings.

        """
        self.logger = logging.getLogger('playbook')
        self.cmdconfig = cmdconfig
        self.output = logging.getLogger("output")
        CmdVars.__init__(self, variablestore)
        ExitOnError.__init__(self)

    def run(self, command: BaseCommand):
        """ Execute the command

        This method is executed by AttackMate and
        executes the given command. This method sets the
        run_count to 1 and runs the method exec(). Please note
        that this function will exchange all variables of the BaseCommand
        with the values of the VariableStore!

        Parameters
        ----------
        command : BaseCommand
            The settings for the command to execute

        """
        if command.only_if:
            if not Conditional.test(self.varstore.substitute(command.only_if, True)):
                if hasattr(command, "type"):
                    self.logger.warn(f"Skipping {command.type}: {command.cmd}")
                else:
                    self.logger.warn(f"Skipping {command.cmd}")
                return
        self.run_count = 1
        self.logger.debug(f"Template-Command: '{command.cmd}'")
        self.exec(self.replace_variables(command))

    def log_command(self, command):
        """ Log starting-status of the command

        """
        self.logger.info(f"Executing '{command}'")

    def save_output(self, command: BaseCommand, result: Result):
        """ Save output of command to a file. This method will
            ignore all exceptions and won't stop the programm
            on error.
        """
        if command.save:
            try:
                with open(command.save, "w") as outfile:
                    outfile.write(result.stdout)
            except Exception as e:
                self.logger.warn(f"Unable to write output to file {command.save}: {e}")

    def exec(self, command: BaseCommand):
        try:
            self.log_command(command)
            result = self._exec_cmd(command)
        except ExecException as error:
            result = Result(error, 1)
        self.exit_on_error(command, result)
        self.set_result(result)
        self.output.info(f"Command: {command.cmd}\n{result.stdout}")
        self.save_output(command, result)
        self.error_if_or_not(command, result)
        self.loop_if(command, result)
        self.loop_if_not(command, result)

    def loop_if(self, command: BaseCommand, result: Result):
        if command.loop_if is not None:
            m = re.search(command.loop_if, result.stdout, re.MULTILINE)
            if m is not None:
                self.logger.warn(
                        f"Re-run command because loop_if matches: {m.group(0)}"
                        )
                if self.run_count < self.variable_to_int("loop_count", command.loop_count):
                    self.run_count = self.run_count + 1
                    time.sleep(self.cmdconfig.loop_sleep)
                    self.exec(command)
                else:
                    self.logger.error("Exitting because loop_count exceeded")
                    exit(1)
            else:
                self.logger.debug("loop_if does not match")

    def loop_if_not(self, command: BaseCommand, result: Result):
        if command.loop_if_not is not None:
            m = re.search(command.loop_if_not, result.stdout, re.MULTILINE)
            if m is None:
                self.logger.warn(
                        "Re-run command because loop_if_not does not match"
                        )
                if self.run_count < self.variable_to_int("loop_count", command.loop_count):
                    self.run_count = self.run_count + 1
                    time.sleep(self.cmdconfig.loop_sleep)
                    self.exec(command)
                else:
                    self.logger.error("Exitting because loop_count exceeded")
                    exit(1)
            else:
                self.logger.debug("loop_if_not does not match")

    def _exec_cmd(self, command: Any) -> Result:
        return Result(None, None)
