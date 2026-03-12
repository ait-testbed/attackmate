from typing import Dict, Tuple, Optional
from attackmate.schemas.base import BaseCommand


class CommandRegistry:
    """Registry mapping command types (and optional ``cmd`` values) to command classes.

    Command classes are registered via the :meth:`register` decorator. The registry
    supports two lookup keys:

    - **type only** — e.g. ``"shell"`` maps to :class:`ShellCommand`.
    - **type + cmd** — e.g. ``("sliver", "cd")`` maps to a more specific class.

    The more specific ``(type, cmd)`` key takes precedence over the ``type``-only key.
    """
    _type_registry: Dict[str, BaseCommand] = {}
    _type_cmd_registry: Dict[Tuple[str, str], BaseCommand] = {}

    @classmethod
    def register(cls, type_: str, cmd: Optional[str] = None):
        """Decorator to register a command class.

        :param type_: The command type string (e.g. ``"shell"``, ``"sleep"``).
        :param cmd: An optional ``cmd`` value for more specific registration.
            If provided, the class is registered under ``(type_, cmd)`` and will
            only be returned when both match. This is a LEGACY pattern and should **NOT** be used anymore.

        Example::

            @CommandRegistry.register("shell")
            class ShellCommand(BaseCommand):
                ...
        """

        def decorator(command_class: BaseCommand):
            if cmd:
                cls._type_cmd_registry[(type_, cmd)] = command_class
            else:
                cls._type_registry[type_] = command_class
            return command_class

        return decorator

    @classmethod
    def get_command_class(cls, type_: str, cmd: Optional[str] = None):
        """Look up a registered command class.

        The ``(type_, cmd)`` key is checked first; if not found, falls back to
        the ``type_``-only key.

        :param type_: The command type string.
        :param cmd: An optional ``cmd`` value for specific lookup.
        :returns: The registered command class.
        :raises ValueError: If no class is registered for the given type and cmd.
        """
        if cmd and (type_, cmd) in cls._type_cmd_registry:
            return cls._type_cmd_registry[(type_, cmd)]
        if type_ in cls._type_registry:
            return cls._type_registry[type_]
        raise ValueError(f"No command registered for type '{type_}' and cmd '{cmd}'")


# Command interface
class Command:
    """Factory interface for creating command instances.

    Command classes are looked up from the :class:`CommandRegistry` based on
    ``type`` and optionally ``cmd``, then instantiated with the remaining keyword
    arguments.
    """
    @staticmethod
    def create(type: str, cmd: Optional[str] = None, **kwargs):
        """Create and return a command instance.

        Looks up the appropriate command class via :class:`CommandRegistry` and
        instantiates it with the provided arguments.

        :param type: The command type (e.g. ``"shell"``, ``"sleep"``, ``"debug"``).
        :param cmd: An optional ``cmd`` value used for more specific class lookup.
        :param kwargs: Additional keyword arguments passed to the command class
            constructor (e.g. ``seconds``, ``varstore``).
        :returns: An instance of the resolved command class.
        :raises ValueError: If no command class is registered for the given
            ``type`` and ``cmd`` combination.

        Example::

            command = Command.create(type="sleep", cmd="sleep", seconds="1")
            command = Command.create(type="debug", cmd="$TEST", varstore=True)
        """
        CommandClass = CommandRegistry.get_command_class(type, cmd)
        return CommandClass(type=type, cmd=cmd, **kwargs)
