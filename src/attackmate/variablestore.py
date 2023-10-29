from string import Template
from typing import Any, Optional


class VariableStore:
    def __init__(self):
        self.clear()

    def clear(self):
        self.variables = {}

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
                return ""
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
