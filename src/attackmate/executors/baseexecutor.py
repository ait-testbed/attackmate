import logging
import json
from datetime import datetime
from typing import Any, Optional
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
                # Recorded rather than dropped: a skipped step used to be absent
                # from the log altogether, which is indistinguishable from a step
                # that was never in the playbook.
                skipped_at = datetime.now().isoformat()
                self.log_json(self.json_logger, command, skipped_at, skipped=True)
                return Result(None, None)
        self.reset_run_count()
        self.logger.debug(f"Template-Command: '{command.cmd}'")
        if command.background:
            # Background commands always return Result('Command started in background', 0)
            time_of_execution = datetime.now().isoformat()
            self.log_json(self.json_logger, command, time_of_execution)
            await self.exec_background(
                self.substitute_template_vars(command, self.substitutes_cmd_vars(command))
            )
            # the background command will return immidiately with Result('Command started in background', 0)
            # Return 0 instead of None so the API/Remote Client sees success
            result = Result('Command started in background', 0)
        else:
            result = await self.exec(
                self.substitute_template_vars(command, self.substitutes_cmd_vars(command))
            )
        return result

    def substitutes_cmd_vars(self, command) -> bool:
        """Whether ``cmd`` should be templated for this command.

        Both the executor and the command get a say, and either can say no.
        ``LoopExecutor`` turns it off for a whole loop body so each iteration
        re-substitutes; a command turns it off to run exactly what the playbook
        says. That matters because ``string.Template`` collapses ``$$`` to a
        single ``$``, and in a shell ``$$`` is the process id - so ``kill -9
        $$`` and ``/tmp/f.$$`` are silently rewritten, and the audit log records
        the rewritten form.
        """
        return self.substitute_cmd_vars and getattr(command, 'substitute_cmd_vars', True)

    def log_command(self, command):
        """Log the start of a command execution at INFO level."""
        self.logger.info(f"Executing '{command}'")

    def log_metadata(self, logger: logging.Logger, command):
        """Log command metadata as a JSON string, if present."""
        if command.metadata:
            logger.info(f'Metadata: {json.dumps(command.metadata)}')

    @staticmethod
    def build_result(command, output, exit_status=None) -> Result:
        """Build a Result, honouring the command's ``use_exit_code`` opt-in.

        The real status is always carried in ``exit_status`` so it reaches the
        audit log. ``returncode`` - which is what ``exit_on_error`` acts on -
        keeps its historical value of ``0`` unless the command opts in, because
        making a true status authoritative by default would start failing
        playbooks that have always passed.
        """
        returncode = 0
        if getattr(command, 'use_exit_code', False) and exit_status is not None:
            returncode = exit_status
        return Result(output, returncode, exit_status=exit_status)

    @staticmethod
    def duration_seconds(start: str, end: str):
        """Seconds between two ISO 8601 timestamps, or None if unparseable."""
        try:
            return round(
                (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds(), 6
            )
        except (TypeError, ValueError):
            return None

    def log_json(self, logger: logging.Logger, command, time, end_time=None,
                 result: Optional[Result] = None, skipped: bool = False):
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
        end_time : str, optional
            ISO 8601 timestamp of when the command finished. Absent for a
            command dispatched to the background, which has not finished.
        result : Result, optional
            The result of the command, used for its return code.
        skipped : bool, optional
            Record the step as skipped by its ``only_if`` condition. Such
            steps used to be left out of the log entirely, which made a
            skipped step indistinguishable from one that never existed.
        """
        command_dict = self.make_command_serializable(
            command, time, end_time=end_time, result=result, skipped=skipped
        )

        try:
            logger.info(json.dumps(command_dict))
        except TypeError as e:
            logger.warning(
                'Failed to serialize object to JSON. '
                'Ensure only basic data types (str, int, float, bool, list, dict) are used. '
                'Error details: %s',
                e,
            )

    def make_command_serializable(self, command, time, end_time=None,
                                  result: Optional[Result] = None, skipped: bool = False):
        command_dict = OrderedDict()
        command_dict['start-datetime'] = time
        # Without an end time, everything about what a step actually did has to
        # be reconstructed elsewhere - and an interactive step returns after a
        # silence, not on exit, so its children can still be running long after
        # the log says it finished.
        if end_time is not None:
            command_dict['end-datetime'] = end_time
            command_dict['duration-seconds'] = self.duration_seconds(time, end_time)
        if skipped:
            command_dict['skipped'] = True
        if hasattr(command, 'type'):
            command_dict['type'] = command.type
        command_dict['cmd'] = command.cmd
        if result is not None:
            # None where no real status exists: inside a live session the shell
            # is still running, so there is nothing to report unless the command
            # asked for wait_for_exit. Never faked as 0.
            command_dict['exit-status'] = getattr(result, 'exit_status', None)
            command_dict['returncode'] = result.returncode

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
        # Bound before the try: log_command can itself raise an ExecException
        # (a non-numeric ssh port reaches variable_to_int through cache_settings),
        # and the logging below would then die with UnboundLocalError.
        time_of_execution = datetime.now().isoformat()
        result = None
        try:
            self.log_command(command)
            self.log_metadata(self.logger, command)
            result = await self._exec_cmd(command)
        except ExecException as error:
            result = Result(str(error), 1)
        finally:
            # In a finally so that a step killed by an uncaught exception is
            # still recorded. It used to be written only on the way out, so the
            # run artifact showed a playbook that simply stopped, with no trace
            # of the step that ended it - which is exactly how a dropped reverse
            # shell presents.
            self.log_json(
                self.json_logger, command, time_of_execution,
                end_time=datetime.now().isoformat(), result=result,
            )
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
