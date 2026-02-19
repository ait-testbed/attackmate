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

    The BaseExecutor is the base class of all Executors.
    It enables base functionality for all Executors and
    provides a structure for all Executors.

    In order to create a custom Executor, one must simply
    derive from the BaseExecutor and implement the method
    _exec_cmd()

    """

    def __init__(
            self,
            pm: ProcessManager,
            varstore: VariableStore,
            cmdconfig=CommandConfig(),
            substitute_cmd_vars=True,
            is_api_instance: bool = False):
        """Constructor for BaseExecutor
        Parameters
        ----------
        pm : ProcessManager
            Process manager instance.
        varstore : VariableStore
            Variable store instance.
        cmdconfig : CommandConfig, default `None`
            Command configuration settings.
        substitute_cmd_vars : bool, default `True`
            Flag to enable or disable variable substitution in command.cmd
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
        """Execute the command

        This method is executed by AttackMate and
        executes the given command. This method sets the
        run_count to 1 and runs the method exec(). Please note
        that this function will exchange all variables of the BaseCommand
        with the values of the VariableStore if substitute_cmd_vars is True!

        Parameters
        ----------
        command : BaseCommand
            The settings for the command to execute

        """
        self.is_api_instance = is_api_instance
        if command.only_if:
            if not Conditional.test(self.varstore.substitute(command.only_if, True)):
                self.logger.info(f'Skipping {getattr(command, "type", "")}({command.cmd})')
                return Result(None, None)
        self.reset_run_count()
        self.logger.debug(f"Template-Command: '{command.cmd}'")
        if command.background:
            # Background commands always return Result(None,None)
            time_of_execution = datetime.now().isoformat()
            self.log_json(self.json_logger, command, time_of_execution)
            await self.exec_background(
                self.substitute_template_vars(command, self.substitute_cmd_vars)
            )
            # the background command will return immidiately with Result(None, None)
            # Return 0 instead of None so the API/Remote Client sees success
            result = Result('Command started in background', 0)
        else:
            result = await self.exec(
                self.substitute_template_vars(command, self.substitute_cmd_vars)
            )
        return result

    def log_command(self, command):
        """Log starting-status of the command"""
        self.logger.info(f"Executing '{command}'")

    def log_metadata(self, logger: logging.Logger, command):
        """Log metadata of the command"""
        if command.metadata:
            logger.info(f'Metadata: {json.dumps(command.metadata)}')

    def log_json(self, logger: logging.Logger, command, time):
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
        """Save output of command to a file. This method will
        ignore all exceptions and won't stop the programm
        on error.
        """
        if command.save:
            try:
                with open(command.save, 'w') as outfile:
                    outfile.write(result.stdout)
            except Exception as e:
                self.logger.warning(f'Unable to write output to file {command.save}: {e}')

    async def exec(self, command: BaseCommand) -> Result:
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
        return Result(None, None)
