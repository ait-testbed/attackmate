from string import Template
import re
import os
from typing import Any, Optional


class ListParseException(Exception):
    """Exception for all List-Parser

    This exception is raised by parse_list if anything
    goes wrong.
    """

    pass


class VariableNotFound(Exception):
    """Exception for all List-Parser

    This exception is raised by get_variable if the
    variable does not exist in the variablestore.
    """

    pass


class ListTemplate(Template):
    idpattern = r'(?a:[\[\]_a-z][\[\]_a-z0-9]*)'


class VariableStore:
    def __init__(self):
        self.clear()

    def clear(self):
        self.lists: dict[str, list[str]] = {}
        self.variables: dict[str, str] = {}

    @classmethod
    def is_list(cls, variable: str) -> bool:
        if re.search(r'\[[0-9]+\]\Z', variable):
            return True
        else:
            return False

    @classmethod
    def parse_list(cls, variable: str) -> tuple[str, int]:
        parsed = re.search(r'\A([^\[\]]+)\[([0-9]+)\]\Z', variable)

        if parsed is None:
            raise ListParseException('List could not be parsed')

        if parsed.group(2) is None:
            raise ListParseException('List-value is None')
        else:
            list_name, index_str = parsed.groups()

        return (list_name, int(index_str))

    def get_lists_variables(self) -> dict[str, str]:
        all_indexed_list_vars = {}
        for list_name, list in self.lists.items():
            for index, value in enumerate(list):
                all_indexed_list_vars[f'{list_name}[{str(index)}]'] = value
        return all_indexed_list_vars

    def from_dict(self, variables: Optional[dict]):
        if isinstance(variables, dict):
            for k, v in variables.items():
                self.set_variable(k, v)

    def remove_sign(self, name: str, sign: str = '$') -> str:
        if name.startswith(sign):
            return name[1:]
        else:
            return name

    def get_list(self, listname: str) -> list[str]:
        name = self.remove_sign(listname)
        if name in self.lists:
            return self.lists[name]
        else:
            raise VariableNotFound

    def get_str(self, variable: str) -> str:
        name = self.remove_sign(variable)
        if name in self.variables:
            return self.variables[name]
        else:
            raise VariableNotFound

    def substitute_str(self, template_str: str, blank: bool = False) -> str:
        temp = ListTemplate(template_str)
        if blank:
            try:
                return temp.substitute(self.variables | self.get_lists_variables())
            except KeyError:
                return ''
        else:
            return temp.safe_substitute(self.variables | self.get_lists_variables())

    def set_variable(self, variable: str, value: str | list[str]):
        if isinstance(value, int):
            value = str(value)
        if isinstance(variable, str):
            varname = self.remove_sign(variable)
            if isinstance(value, str):
                if self.is_list(varname):
                    list_name, index = self.parse_list(varname)
                    self.lists[list_name][index] = value
                else:
                    self.variables[varname] = value
            if isinstance(value, list):
                self.lists[varname] = list(value)

    def get_variable(self, variable: str) -> str | list[str]:
        if variable in self.variables:
            return self.variables[variable]
        if variable in self.lists:
            return self.lists[variable]
        raise VariableNotFound

    def substitute(self, data: Any, blank: bool = False) -> Any:
        if isinstance(data, str):
            return self.substitute_str(data, blank)
        else:
            return data

    def get_prefixed_env_vars(self, prefix: str = 'ATTACKMATE_') -> dict[str, str]:
        prefixed_env_vars = {k[len(prefix) :]: v for k, v in os.environ.items() if k.startswith(prefix)}
        return prefixed_env_vars

    def replace_with_prefixed_env_vars(self):
        """Replaces the current variables with corresponding prefixed environment variables if they exist."""
        env_vars = self.get_prefixed_env_vars()

        for var_name in list(self.variables.keys()):
            if var_name in env_vars:
                self.set_variable(var_name, env_vars[var_name])
