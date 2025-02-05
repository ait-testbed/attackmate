from typing import Dict, Tuple, Optional
from attackmate.schemas.base import BaseCommand


class CommandRegistry:
    _type_registry: Dict[str, BaseCommand] = {}
    _type_cmd_registry: Dict[Tuple[str, str], BaseCommand] = {}

    @classmethod
    def register(cls, type_: str, cmd: Optional[str] = None):
        """register a command class by type or type + cmd."""

        def decorator(command_class: BaseCommand):
            if cmd:
                cls._type_cmd_registry[(type_, cmd)] = command_class
            else:
                cls._type_registry[type_] = command_class
            return command_class

        return decorator

    @classmethod
    def get_command_class(cls, type_: str, cmd: Optional[str] = None):
        """Retrieve the command class based on type or type + cmd."""
        if cmd and (type_, cmd) in cls._type_cmd_registry:
            return cls._type_cmd_registry[(type_, cmd)]
        if type_ in cls._type_registry:
            return cls._type_registry[type_]
        raise ValueError(f"No command registered for type '{type_}' and cmd '{cmd}'")


# Command interface
class Command:
    @staticmethod
    def create(type: str, cmd: Optional[str] = None, **kwargs):
        """return a command instance based on type and cmd."""
        CommandClass = CommandRegistry.get_command_class(type, cmd)
        return CommandClass(type=type, cmd=cmd, **kwargs)
