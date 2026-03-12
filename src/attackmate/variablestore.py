from string import Template
import re
import os
from typing import Any, Optional


class ListParseException(Exception):
    """Exception for all List-Parser

    This exception is raised by parse_list if anything
    goes wrong.
    """


class VariableNotFound(Exception):
    """Exception for all List-Parser

    This exception is raised by get_variable if the
    variable does not exist in the variablestore.
    """


class ListTemplate(Template):
    idpattern = r'(?a:[\[\]_a-z][\[\]_a-z0-9]*)'


class VariableStore:
    """Stores and resolves variables for use in AttackMate playbooks.

    Variables are held in two separate namespaces:

    - **Scalar variables** — simple string key-value pairs, accessed as ``$varname``.
    - **List variables** — ordered sequences of strings, accessed by index as
      ``$varname[0]``, ``$varname[1]``, etc.

    All values are stored as plain Python ``str``, regardless of their original type.
    Integer values are coerced to ``str`` on ingress. Variable substitution uses
    Python's :class:`string.Template` syntax.

    If an environment variable prefixed with ``ATTACKMATE_`` exists with the same name
    as a stored variable, it will override the stored value when
    :meth:`replace_with_prefixed_env_vars` is called.

    Example::

        store = VariableStore()
        store.set_variable("HOST", "192.168.1.1")
        store.substitute_str("Target: $HOST")  # returns "Target: 192.168.1.1"
    """

    def __init__(self):
        self.clear()

    def clear(self):
        """Reset the store, removing all scalar variables and lists."""
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
        """Populate the store from a dictionary.

        Each key-value pair is passed to :meth:`set_variable`. Keys may optionally
        include a leading ``$``, which is stripped before storing.

        :param variables: A dictionary of variable names to values. Non-dict values
            are silently ignored.
        """
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
        """Substitute all ``$variable`` references in a template string.

        Resolves both scalar variables and indexed list variables
        (e.g. ``$mylist[0]``).

        :param template_str: A string containing ``$variable`` placeholders.
        :param blank: If ``True``, unresolved references are replaced with ``''``
            and a :exc:`KeyError` causes the entire result to be ``''``.
            If ``False`` (default), unresolved references are left as-is.
        :returns: The string with all known variables substituted.
        """
        temp = ListTemplate(template_str)
        if blank:
            try:
                return temp.substitute(self.variables | self.get_lists_variables())
            except KeyError:
                return ''
        else:
            return temp.safe_substitute(self.variables | self.get_lists_variables())

    def set_variable(self, variable: str, value: str | list[str]):
        """Store a variable by name.

        If ``value`` is an ``int`` it is coerced to ``str`` before storing.
        If ``variable`` refers to a list index (e.g. ``mylist[0]``), the value
        is written into the corresponding position of the existing list.
        If ``value`` is a ``list``, it is stored as a list variable.

        :param variable: The variable name, with or without a leading ``$``.
        :param value: The value to store. Integers are coerced to ``str``.
        """
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
        """Retrieve a variable by name.

        Checks scalar variables first, then list variables.

        :param variable: The variable name (without ``$`` prefix).
        :returns: The stored ``str`` value or ``list[str]``.
        :raises VariableNotFound: If no variable with that name exists.
        """
        if variable in self.variables:
            return self.variables[variable]
        if variable in self.lists:
            return self.lists[variable]
        raise VariableNotFound

    def substitute(self, data: Any, blank: bool = False) -> Any:
        """Substitute variables in ``data`` if it is a string.

        Non-string values are returned unchanged.

        :param data: The value to substitute into. Only ``str`` values are processed.
        :param blank: If ``True``, unresolved variable references are replaced with
            an empty string. If ``False`` (default), they are left as-is.
        :returns: The substituted string, or the original value if not a string.
        """
        if isinstance(data, str):
            return self.substitute_str(data, blank)
        else:
            return data

    def get_prefixed_env_vars(self, prefix: str = 'ATTACKMATE_') -> dict[str, str]:
        """Return all environment variables that start with ``prefix``, stripped of the prefix.

        :param prefix: The prefix to filter and strip. Defaults to ``'ATTACKMATE_'``.
        :returns: A dictionary mapping unprefixed names to their environment values.
        """
        prefixed_env_vars = {k[len(prefix):]: v for k, v in os.environ.items() if k.startswith(prefix)}
        return prefixed_env_vars

    def replace_with_prefixed_env_vars(self):
        """Override stored variables with matching prefixed environment variables.

        For each scalar variable currently in the store, if an environment variable
        named ``ATTACKMATE_<varname>`` exists, its value replaces the stored one.

        Example: the stored variable ``FOO`` is overridden by the environment
        variable ``ATTACKMATE_FOO`` if it is set.
        """
        env_vars = self.get_prefixed_env_vars()

        for var_name in list(self.variables.keys()):
            if var_name in env_vars:
                self.set_variable(var_name, env_vars[var_name])
