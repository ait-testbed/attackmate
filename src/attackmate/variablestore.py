from string import Template
import re
from typing import Any, Optional


class ListParseException(Exception):
    """ Exception for all List-Parser

    This exception is raised by parse_list if anything
    goes wrong.
    """
    pass


class VariableStore:
    def __init__(self):
        self.clear()

    def clear(self):
        self.lists: dict[str, list[str]] = {}
        self.variables = {}

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

    def from_dict(self, variables: Optional[dict]):
        if isinstance(variables, dict):
            for k, v in variables.items():
                name = self.remove_sign(k)
                self.variables[name] = v

    def remove_sign(self, name: str, sign: str = '$') -> str:
        if name.startswith(sign):
            return name[1:]
        else:
            return name

    def substitute_str(self, template_str: str, blank: bool = False) -> str:
        temp = Template(template_str)
        if blank:
            try:
                return temp.substitute(self.variables)
            except KeyError:
                return ''
        else:
            return temp.safe_substitute(self.variables)

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
                self.lists[varname] = value

    def get_variable(self, variable: str):
        return self.variables[variable]

    def substitute(self, data: Any, blank: bool = False) -> Any:
        if isinstance(data, str):
            return self.substitute_str(data, blank)
        else:
            return data
