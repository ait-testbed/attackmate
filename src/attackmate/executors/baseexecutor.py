import logging
import json
from datetime import datetime
from typing import Any
from collections import OrderedDict

from pydantic import BaseModel
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.executors.features.exitonerror import ExitOnError
from attackmate.executors.features.looper import Looper
from attackmate.executors.features.background import Background
from attackmate.executors.features.conditional import Conditional
from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.config import CommandConfig
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


class BaseExecutor(ExitOnError, CmdVars, Looper, Background):
    """
    Base class for all AttackMate executors.

    Provides the core execution pipeline for commands, including variable
    substitution, conditional execution (``only_if``), background mode,
    loop control (``loop_if`` / ``loop_if_not``), error handling, output
    logging, and JSON audit logging.

    To implement a custom executor, subclass ``BaseExecutor`` and override
    :meth:`_exec_cmd`. All other pipeline behaviour is inherited.

    Example::

        class MyExecutor(BaseExecutor):
            async def _exec_cmd(self, command: MyCommand) -> Result:
                output = run_my_tool(command.cmd)
                return Result(stdout=output, returncode=0)

    """

    def __init__(
            self,
            pm: ProcessManager,
            varstore: VariableStore,
            cmdconfig=CommandConfig(),
            substitute_cmd_vars=True,
            is_api_instance: bool = False):
        """
        Initialise the executor with shared infrastructure.

        Parameters
        ----------
        pm : ProcessManager
            Process manager used to track and clean up background processes.
        varstore : VariableStore
            Variable store used for template substitution in commands.
        cmdconfig : CommandConfig, optional
            Global command configuration (e.g. delays, loop defaults).
            Defaults to an empty ``CommandConfig``.
        substitute_cmd_vars : bool, optional
            If ``True`` (default), variable references in ``command.cmd``
            are substituted from the variable store before execution.
        is_api_instance : bool, optional
            If ``True``, suppresses ``exit_on_error`` behaviour so that
            API callers receive errors as results rather than process exits.
        """

        Background.__init__(self, pm)
        CmdVars.__init__(self, varstore)
        ExitOnError.__init__(self)
        Looper.__init__(self, cmdconfig)
        self.logger = logging.getLogger('playbook')
        self.json_logger = logging.getLogger('json')
        self.cmdconfig = cmdconfig
        self.output = logging.getLogger('output')
        self.substitute_cmd_vars = substitute_cmd_vars
        self.is_api_instance = is_api_instance

    async def run(self, command: BaseCommand, is_api_instance: bool = False) -> Result:
        """
        Entry point for executing a command.

        Called by AttackMate for each command in the playbook. Evaluates the
        ``only_if`` condition first and skips the command if it is not met.
        In background mode, the command is dispatched asynchronously and
        returns immediately with a placeholder result. Otherwise, the full
        synchronous execution pipeline is run via :meth:`exec`.

        Parameters
        ----------
        command : BaseCommand
            The command to execute, including all configured options.
        is_api_instance : bool, optional
            Overrides the instance-level ``is_api_instance`` flag for this
            execution. Defaults to ``False``.

        Returns
        -------
        Result
            The result of the command execution, containing stdout and
            return code. Returns ``Result(None, None)`` if the ``only_if``
            condition is not met.
        """
        self.is_api_instance = is_api_instance
        if command.only_if:
            if not Conditional.test(self.varstore.substitute(command.only_if, True)):
                self.logger.info(f'Skipping {getattr(command, "type", "")}({command.cmd})')
                return Result(None, None)
        self.reset_run_count()
        self.logger.debug(f"Template-Command: '{command.cmd}'")
        if command.background:
            # Background commands always return Result('Command started in background', 0)
            time_of_execution = datetime.now().isoformat()
            self.log_json(self.json_logger, command, time_of_execution)
            await self.exec_background(
                self.substitute_template_vars(command, self.substitute_cmd_vars)
            )
            # the background command will return immidiately with Result('Command started in background', 0)
            # Return 0 instead of None so the API/Remote Client sees success
            result = Result('Command started in background', 0)
        else:
            result = await self.exec(
                self.substitute_template_vars(command, self.substitute_cmd_vars)
            )
        return result

    def log_command(self, command):
        """Log the start of a command execution at INFO level."""
        self.logger.info(f"Executing '{command}'")

    def log_metadata(self, logger: logging.Logger, command):
        """Log command metadata as a JSON string, if present."""
        if command.metadata:
            logger.info(f'Metadata: {json.dumps(command.metadata)}')

    def log_json(self, logger: logging.Logger, command, time):
        """
        Serialize a command to JSON and write it to the JSON audit log.

        If serialization fails due to non-serializable types, a warning is
        logged instead and execution continues.

        Parameters
        ----------
        logger : logging.Logger
            The logger to write the JSON entry to.
        command : BaseCommand
            The command to serialize.
        time : str
            ISO 8601 timestamp of when the command started.
        """
        command_dict = self.make_command_serializable(command, time)

        try:
            logger.info(json.dumps(command_dict))
        except TypeError as e:
            logger.warning(
                'Failed to serialize object to JSON. '
                'Ensure only basic data types (str, int, float, bool, list, dict) are used. '
                'Error details: %s',
                e,
            )

    def make_command_serializable(self, command, time):
        command_dict = OrderedDict()
        command_dict['start-datetime'] = time
        if hasattr(command, 'type'):
            command_dict['type'] = command.type
        command_dict['cmd'] = command.cmd

        command_dict['parameters'] = dict()
        for key, value in command.__dict__.items():
            if key not in command_dict and key != 'commands' and key != 'remote_command':
                command_dict['parameters'][key] = value
            # Handle nested "commands" recursively
            if key == 'commands' and isinstance(value, list):
                command_dict['parameters']['commands'] = [
                    self.make_command_serializable(sub_command, time) for sub_command in value
                ]
            if key == 'remote_command' and isinstance(value, BaseModel):
                command_dict['parameters']['remote_command'] = self.make_command_serializable(value, time)
        return command_dict

    def save_output(self, command: BaseCommand, result: Result):
        """
        Write command output to a file if ``command.save`` is set.

        Failures are logged as warnings and do not interrupt execution.

        Parameters
        ----------
        command : BaseCommand
            The command whose output should be saved.
        result : Result
            The result containing the stdout to write.
        """
        if command.save:
            try:
                with open(command.save, 'w') as outfile:
                    outfile.write(result.stdout)
            except Exception as e:
                self.logger.warning(f'Unable to write output to file {command.save}: {e}')

    async def exec(self, command: BaseCommand) -> Result:
        """
        Run the full synchronous execution pipeline for a command.

        Calls :meth:`_exec_cmd`, then handles JSON logging, output saving,
        error checking, variable store updates, and loop condition evaluation.

        Parameters
        ----------
        command : BaseCommand
            The command to execute.

        Returns
        -------
        Result
            The result of the command, or a ``Result(str(error), 1)`` if an
            :class:`~attackmate.execexception.ExecException` is raised.
        """
        try:
            self.log_command(command)
            self.log_metadata(self.logger, command)
            time_of_execution = datetime.now().isoformat()
            result = await self._exec_cmd(command)
        except ExecException as error:
            result = Result(str(error), 1)
        self.log_json(self.json_logger, command, time_of_execution)
        self.save_output(command, result)
        if not command.background:
            if not self.is_api_instance:
                self.exit_on_error(command, result)
            self.set_result_vars(result)
            self.output.info(f'Command: {command.cmd}\n{result.stdout}')
            self.error_if_or_not(command, result)
        await self.loop_if(command, result)
        await self.loop_if_not(command, result)
        return result

    async def _loop_exec(self, command: BaseCommand) -> Result:
        result = await self.exec(command)
        return result

    async def _exec_cmd(self, command: Any) -> Result:
        """
        Execute the command. Override this method in subclasses.

        This is the only method that must be implemented in a custom executor.
        The base implementation is a no-op that returns ``Result(None, None)``.

        Parameters
        ----------
        command : Any
            The command to execute. Subclasses should type this as their
            specific command schema class.

        Returns
        -------
        Result
            The result of the command execution.
        """
        return Result(None, None)
