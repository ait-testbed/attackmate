import re
import time
import logging
from .schemas import BaseCommand
from typing import Any


class ExecException(Exception):
    """ Exception for all Executors

    This exception is raised by Executors if anything
    goes wrong. The BaseExecutor will catch the
    Exception, writes it to the console and exits
    gracefully.

    """
    pass


class Result:
    """

    Instances of this Result-class will be returned
    by the Executors. It stores the standard-output
    and the returncode.
    """
    stdout: str
    returncode: int

    def __init__(self, stdout, returncode):
        """ Constructor of the Result

        Instances of this Result-class will be returned
        by the Executors. It stores the standard-output
        and the returncode.

        Parameters
        ----------
        stdout : str
            The standard-output of a command.
        returncode : int
            The returncode of a previous executed command
        """
        self.stdout = stdout
        self.returncode = returncode


class BaseExecutor:
    """

    The BaseExecutor is the base class of all Executors.
    It enables base functionality for all Executors and
    provides a structure for all Executors.

    In order to create a custom Executor, one must simply
    derive from the BaseExecutor and implement the method
    _exec_cmd()

    """
    def __init__(self, cmdconfig=None):
        """ Constructor for BaseExecutor

        Parameters
        ----------
        cmdconfig : str, default `None`
            cmd_config settings.

        """
        self.logger = logging.getLogger('playbook')
        self.cmdconfig = cmdconfig
        self.output = logging.getLogger("output")

    def run(self, command: BaseCommand):
        """ Execute the command

        This method is executed by PenPal and
        executes the given command. This method sets the
        run_count to 1 and runs the method exec()

        Parameters
        ----------
        command : BaseCommand
            The settings for the command to execute

        """
        self.run_count = 1
        self.exec(command)

    def log_command(self, command):
        """ Log starting-status of the command

        """
        self.logger.info(f"Executing '{command}'")

    def exec(self, command: BaseCommand):
        try:
            self.log_command(command)
            result = self._exec_cmd(command)
        except ExecException as error:
            result = Result(error, 1)
        if result.returncode != 0:
            self.logger.error(result.stdout)
            exit(1)
        self.output.info(f"Command: {command.cmd}\n{result.stdout}")
        self.error_if(command, result)
        self.error_if_not(command, result)
        self.loop_if(command, result)
        self.loop_if_not(command, result)

    def error_if(self, command: BaseCommand, result: Result):
        if command.error_if is not None:
            m = re.search(command.error_if, result.stdout, re.MULTILINE)
            if m is not None:
                self.logger.error(
                        f"Exitting because error_if matches: {m.group(0)}"
                        )
                exit(1)

    def error_if_not(self, command: BaseCommand, result: Result):
        if command.error_if_not is not None:
            m = re.search(command.error_if_not, result.stdout, re.MULTILINE)
            if m is None:
                self.logger.error(
                        "Exitting because error_if_not does not match"
                        )
                exit(1)

    def loop_if(self, command: BaseCommand, result: Result):
        if command.loop_if is not None:
            m = re.search(command.loop_if, result.stdout, re.MULTILINE)
            if m is not None:
                self.logger.warn(
                        f"Re-run command because loop_if matches: {m.group(0)}"
                        )
                if self.run_count < command.loop_count:
                    self.run_count = self.run_count + 1
                    time.sleep(self.cmdconfig.loop_sleep)
                    self.exec(command)
                else:
                    self.logger.error("Exitting because loop_count exceeded")
                    exit(1)

    def loop_if_not(self, command: BaseCommand, result: Result):
        if command.loop_if_not is not None:
            m = re.search(command.loop_if_not, result.stdout, re.MULTILINE)
            if m is None:
                self.logger.warn(
                        "Re-run command because loop_if_not does not match"
                        )
                if self.run_count < command.loop_count:
                    self.run_count = self.run_count + 1
                    time.sleep(self.cmdconfig.loop_sleep)
                    self.exec(command)
                else:
                    self.logger.error("Exitting because loop_count exceeded")
                    exit(1)

    def _exec_cmd(self, command: Any) -> Result:
        return Result(None, None)
