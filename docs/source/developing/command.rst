.. _command:

======================
Adding a New Command
======================

AttackMate supports extending its functionality by adding new commands.
This section details the steps required to integrate a new command.


1. Define the Command Schema
=============================

All Commands in AttackMate inherit from ``BaseCommand``.
To create a new command, define a class in `/src/attackmate/schemas` and register it using the ``@CommandRegistry.register('<command_type>')`` decorator.

Registering the command in the ``CommandRegistry`` allows the command to be also instantiated dynamically using the ``Command.create()`` method and is essential to
make it usable in external python scripts.

.. note::

   **Registration rules:**

   - Every command class must have a **unique** ``type`` literal — this is the sole discriminator
     used to identify a command in the union.
   - A command may additionally define a ``cmd`` field to express sub-behaviors (e.g.
     ``Literal['file', 'dir']``). In this case, branching on ``cmd`` belongs in the
     **executor**, not in the schema's union discrimination.
   - The ``type`` + ``cmd`` nested union pattern seen in ``SliverSessionCommands`` is
     **legacy** and must not be replicated. New command families must always use a unique
     ``type`` per class.


**Example: a simple command with no sub-behaviors**

.. code-block:: python

    from typing import Literal
    from .base import BaseCommand
    from attackmate.command import CommandRegistry

    @CommandRegistry.register('debug')
    class DebugCommand(BaseCommand):
        type: Literal['debug']
        varstore: bool = False
        exit: bool = False
        wait_for_key: bool = False
        cmd: str = ''


**Example: a command with sub-behaviors expressed via** ``cmd``

.. code-block:: python

    from typing import Literal
    from .base import BaseCommand
    from attackmate.command import CommandRegistry

    @CommandRegistry.register('mktemp')
    class TempfileCommand(BaseCommand):
        type: Literal['mktemp']
        cmd: Literal['file', 'dir'] = 'file'
        variable: str


2. Implement the Command Execution
===================================

The new command should be handled by an executor in `src/attackmate/executors` that extends ``BaseExecutor`` and implements the ``_exec_cmd()`` method. For example:

.. code-block:: python

    from attackmate.executors.base_executor import BaseExecutor
    from attackmate.result import Result
    from attackmate.executors.executor_factory import executor_factory

    @executor_factory.register_executor('debug')
    class DebugExecutor(BaseExecutor):
        async def _exec_cmd(self, command: DebugCommand) -> Result:
            self.logger.info(f"Executing debug command: {command.cmd}")
            return Result(stdout="Debug executed", returncode=0)


3. Ensure the Executor Handles the New Command
==============================================

The ``ExecutorFactory`` class manages and creates executor instances based on command types.
It maintains a registry (``_executors``) that maps command type strings to executor classes, allowing for dynamic execution of different command types.
Executors are registered using the ``register_executor`` method, which provides a decorator to associate a command type with a class.

When a command is executed, the ``create_executor`` method retrieves the corresponding executor class, filters the constructor arguments based on the class's signature, and then creates an instance.

Accordingly, executors must be registered using the ``@executor_factory.register_executor('<command_type>')`` decorator.

.. code-block:: python

    @executor_factory.register_executor('debug')
    class DebugExecutor(BaseExecutor):
        # implementation of the executor


If the new executor class requires additional initialization arguments, these must be added to the ``_get_executor_config`` method in ``attackmate.py``.
All configurations are always passed to the ``ExecutorFactory``.
The factory filters the provided configurations based on the class constructor signature, ensuring that only the required parameters are used.

.. code-block:: python

        def _get_executor_config(self) -> dict:
        config = {
            'pm': self.pm,
            'varstore': self.varstore,
            'cmdconfig': self.pyconfig.cmd_config,
            'msfconfig': self.pyconfig.msf_config,
            'msfsessionstore': self.msfsessionstore,
            'sliver_config': self.pyconfig.sliver_config,
            'runfunc': self._run_commands,
            # if necessary add new config here
        }
        return config

4. Add the Executor to the __init__ file of the attackmate.executors module
===========================================================================

Add the new executor to the __all__ list in the __init__.py file of the attackmate.executors module so it can be imported elsewhere.

.. code-block:: python

    # src/attackmate/executors/__init__.py
    # other imports
    from .shell.shellexecutor import ShellExecutor
    from .metasploit.msfsessionexecutor import CustomExecutor # new executor
    # other imports

    __all__ = [
        'RemoteExecutor',
        'BrowserExecutor',
        'ShellExecutor',
        'CustomExecutor', # new executor
        # other executors
    ]



5. Modify the Loop Command to Include the New Command
=====================================================

in `/src/attackmate/schemas/loop.py` update the ``LoopCommand`` schema to include the new command.

.. code-block:: python

    Command = Union[
            ShellCommand,
            DebugCommand,  # Newly added command
            # ... other command classes ...
        ]


6. Modify the RemotelyExecutableCommand Union to Include the New Command
========================================================================

in `src/attackmate/schemas/command_subtypes.py`, update the ``RemotelyExecutableCommand`` type alias to include the new command

.. code-block:: python

    RemotelyExecutableCommand: TypeAlias = Annotated[
        Union[
            SliverSessionCommands,
            SliverCommands,
            BrowserCommand,
            ShellCommand,
            DebugCommand,  # Newly added command
            # ... other command classes ...
        ],
        Field(discriminator='type'),  # Outer discriminator (type)
    ]

.. note::

   ``RemotelyExecutableCommand`` defines the complete set of commands that can be executed
   on a remote AttackMate instance. It is a Pydantic discriminated union using ``type`` as
   its sole discriminator — every command class must define a unique ``type`` literal, which
   is used to resolve the correct class from the union.

   **Adding a new command to** ``RemotelyExecutableCommand``\ **:**

   Simply add the new command class directly to the ``Union`` in ``RemotelyExecutableCommand``.
   No further schema-level discrimination is needed — any sub-behaviors should be expressed
   via a ``cmd`` field on the class and handled in the executor.

   **Legacy pattern (do not replicate):**

   The nested ``SliverSessionCommands`` and ``SliverCommands`` aliases use a two-level
   discrimination strategy — an outer ``type`` discriminator to identify the command family,
   and an inner ``cmd`` discriminator to resolve the specific sub-command. This follows
   Pydantic's `nested discriminated unions
   <https://docs.pydantic.dev/latest/concepts/unions/#nested-discriminated-unions>`_ pattern
   but couples sub-behavior decisions into the schema layer. New command families must
   **not** replicate this pattern.

Once these steps are completed, the new command will be fully integrated into AttackMate and available for execution.

7. Add Documentation
=====================

Finally, update the documentation in `docs/source/playbook/commands` to include the new command.
