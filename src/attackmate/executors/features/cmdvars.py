import copy

from attackmate.result import Result
from attackmate.schemas.base import BaseCommand, StringNumber
from attackmate.variablestore import VariableStore
from attackmate.execexception import ExecException


class CmdVars:
    def __init__(self, variablestore: VariableStore):
        self.varstore = variablestore
        self.setoutuptvars = True

    def set_result_vars(self, result: Result):
        if self.setoutuptvars:
            self.varstore.set_variable('RESULT_STDOUT', result.stdout)
            self.varstore.set_variable('RESULT_RETURNCODE', str(result.returncode))

    def replace_variables(self, command: BaseCommand) -> BaseCommand:
        """ Replace variables using the VariableStore

        Replace all template-variables of the BaseCommand and return
        a new BaseCommand with all variables replaced with their values.

        Parameters
        ----------
        command : BaseCommand
            BaseCommand where all variables should be replaced

        Returns
        -------
        BaseCommand
            BaseCommand with replaced variables
        """
        template_cmd = copy.deepcopy(command)
        for member in command.list_template_vars():
            cmd_member = getattr(command, member)
            if isinstance(cmd_member, str):
                replaced_str = self.varstore.substitute(cmd_member)
                setattr(template_cmd, member, replaced_str)
            elif isinstance(cmd_member, dict):
                # copy the dict to avoid referencing the original dict
                new_cmd_member = copy.deepcopy(cmd_member)
                for k, v in new_cmd_member.items():
                    if isinstance(v, str):
                        new_cmd_member[k] = self.varstore.substitute(v)
                setattr(template_cmd, member, new_cmd_member)
            elif isinstance(cmd_member, list):
                # copy the dict to avoid referencing the original list
                new_list = [i for i in cmd_member]
                for v in new_list:
                    if isinstance(v, str):
                        index = new_list.index(v)
                        new_list[index] = self.varstore.substitute(v)
                setattr(template_cmd, member, new_list)
        return template_cmd

    @staticmethod
    def variable_to_int(variablename: str, value: StringNumber) -> int:
        if not value:
            raise ExecException(f'Variable {variablename} has not a numeric value: {value}')

        if isinstance(value, int):
            return value

        if value.isnumeric():
            return int(value)
        else:
            raise ExecException(f'Variable {variablename} has not a numeric value: {value}')

    @staticmethod
    def variable_to_bool(variablename: str, value: str) -> bool:
        if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
        if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
        raise ExecException(f'Invalid value for boolean conversion of {variablename}: {value}')
