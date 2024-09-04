from string import Template
import re
from typing import Any, Optional


class ListParseException(Exception):
    """ Exception for all List-Parser

    This exception is raised by parse_list if anything
    goes wrong.
    """
    pass


class VariableNotFound(Exception):
    """ Exception for all List-Parser

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
        [self.variables = {}](self.variables: dict[str, str] = {})

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
            value = parsed.group(2)

        return (parsed.group(1), int(value))

    def get_lists_variables(self) -> dict[str, str]:
        ret = {}

        for k, v in self.lists.items():
            for idx, val in enumerate(v):
                ret[f'{k}[{idx}]'] = val
        return ret

    def from_dict(self, variables: Optional[dict]):
        if isinstance(variables, dict):
            for k, v in variables.items():
                self.set_variable(k, v)

    def remove_sign(self, name: str, sign: str = '$') -> str:
        if name.startswith(sign):
            return name[1:]
        else:
            return name

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
        if isinstance(variable, str):
            varname = self.remove_sign(variable)
            if isinstance(value, str):
                if self.is_list(varname):
                    parsed = self.parse_list(varname)
                    self.lists[parsed[0]][parsed[1]] = value
                else:
                    self.variables[varname] = value
            if isinstance(value, list):
                self.lists[varname] = list(value)

    def get_variable(self, variable: str) -> (str | list[str]):
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
