"""
jsonexecutor.py
============================================
This class allows to load variables from a json file
"""

import json
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.schemas.json import JsonCommand
from attackmate.result import Result
from attackmate.executors.executor_factory import executor_factory
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


@executor_factory.register_executor('json')
class JsonExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, varstore: VariableStore, cmdconfig=None):
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: JsonCommand):
        if command.varstore:
            self.logger.warning(f'Varstore: {self.varstore.variables}')

        self.logger.warning(f"Loading variables from file: '{command.cmd}'")

    def _exec_cmd(self, command: JsonCommand) -> Result:
        try:
            if command.use_var:
                input_var = self.varstore.get_variable(command.cmd)
                # Ensure input_var is a string
                if isinstance(input_var, list):
                    input_var = ''.join(input_var)
                elif not isinstance(input_var, str):
                    # Convert non-string types to string
                    input_var = str(input_var)
                json_data = json.loads(input_var)
                self.logger.info(f'Successfully parsed JSON from {command.cmd}')
            else:
                with open(command.cmd, 'r') as json_file:
                    json_data = json.load(json_file)

                self.logger.info(f"Successfully loaded JSON file: '{command.cmd}'")

            # Populate the variable store
            for k, v in json_data.items():
                self.varstore.set_variable(k.upper(), v)
            if command.varstore:
                self.logger.info(f'Variables updated in VariableStore: {self.varstore.variables}')
                self.logger.info(f'List variables updated in VariableStore: {self.varstore.lists}')

            return Result(json_data, 0)

        except FileNotFoundError:
            error_msg = f"File '{command.cmd}' not found"
            self.logger.error(error_msg)
            return Result(error_msg, 1)

        except json.JSONDecodeError as e:
            error_msg = f"Error parsing JSON file '{command.cmd}': {str(e)}"
            self.logger.error(error_msg)
            return Result(error_msg, 1)

        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            self.logger.error(error_msg)
            return Result(error_msg, 1)
