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
        self.lists = {}
        self.variables = {}

    @classmethod
    def is_list(cls, variable: str) -> bool:
        if re.search(r'\[[^\[]*\]\Z', variable):
            return True
        else:
            return False

    @classmethod
    def parse_list(cls, variable: str) -> tuple[str, str]:
        parsed = re.search(r'\A([^\[\]]+)\[([^\[]*)\]\Z', variable)

        if parsed is None:
            raise ListParseException('List could not be parsed')

        if parsed.group(2) is None:
            raise ListParseException('List-value is None')
        else:
            value = parsed.group(2)

        if value.startswith('"'):
            if value.endswith('"'):
                value = value[1:-1]
            else:
                raise ListParseException('List-value does not end with character "')

        if value.endswith('"'):
            if not value.startswith('"'):
                raise ListParseException('List-value does not start with character "')

        if value.startswith('\''):
            if value.endswith('\''):
                value = value[1:-1]
            else:
                raise ListParseException('List-value does not end with character \'')

        if value.endswith('\''):
            if not value.startswith('\''):
                raise ListParseException('List-value does not start with character \'')

        return (parsed.group(1), value)

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

    def set_variable(self, variable: str, value: str):
        self.variables[self.remove_sign(variable)] = value

    def get_variable(self, variable: str):
        return self.variables[variable]

    def substitute(self, data: Any, blank: bool = False) -> Any:
        if isinstance(data, str):
            return self.substitute_str(data, blank)
        else:
            return data
