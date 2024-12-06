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
        file = command.local_path if command.local_path else command.cmd
        self.logger.warning(f"Loading variables from: '{file}'")

    def flatten_dict(self, nested_json, parent_key='', sep='_'):
        items = []

        for key, value in nested_json.items():
            new_key = f'{parent_key}{sep}{key}' if parent_key else key

            if isinstance(value, dict):
                # Recursively flatten the dictionary
                items.extend(self.flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # Handle lists
                # If the list contains only primitive values (str, int), keep the list as is
                if all(isinstance(i, (str, int)) for i in value):
                    items.append((new_key, value))  # Retain the list as a whole
                else:
                    for i, sub_value in enumerate(value):
                        if isinstance(sub_value, dict):
                            # Recursively flatten each dictionary within the list
                            items.extend(self.flatten_dict(sub_value, f'{new_key}_{i}', sep=sep).items())
                        elif isinstance(sub_value, list):
                            # Recursively flatten a list within a list
                            items.extend(self.flatten_dict(sub_value, f'{new_key}_{i}', sep=sep).items)
                        else:
                            items.append((f'{new_key}_{i}', value))
            else:
                items.append((new_key, value))

        return dict(items)

    def _exec_cmd(self, command: JsonCommand) -> Result:
        try:
            if not command.local_path and command.cmd:
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
                with open(str(command.local_path), 'r') as json_file:
                    json_data = json.load(json_file)

                self.logger.info(f"Successfully loaded JSON file: '{command.local_path}'")

            # Populate the variable store
            for k, v in self.flatten_dict(json_data).items():
                self.varstore.set_variable(k.upper(), v)
            if command.varstore:
                self.logger.info(f'Variables updated in VariableStore: {self.varstore.variables}')
                self.logger.info(f'List variables updated in VariableStore: {self.varstore.lists}')

            return Result(json_data, 0)

        except FileNotFoundError:
            error_msg = f"File '{command.local_path}' not found"
            self.logger.error(error_msg)
            return Result(error_msg, 1)

        except json.JSONDecodeError as e:
            error_msg = f"Error parsing JSON file '{command.local_path}': {str(e)}"
            self.logger.error(error_msg)
            return Result(error_msg, 1)

        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            self.logger.error(error_msg)
            return Result(error_msg, 1)
