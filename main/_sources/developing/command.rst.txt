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

For example, to add a ``debug`` command:

::

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

Registering the command in the ``CommandRegistry`` allows the command to be also instantiated dynamically using the ``Command.create()`` method and is essential to 
make them usable in external python scripts.


2. Implement the Command Execution
===================================

The new command should be handled by an executor in `src/attackmate/executors`` that extends ``BaseExecutor`` and implements the ``_exec_cmd()`` method. For example:

::

    from attackmate.executors.base_executor import BaseExecutor
    from attackmate.result import Result
    from attackmate.executors.executor_factory import executor_factory

    @executor_factory.register_executor('debug')
    class DebugExecutor(BaseExecutor):
        def _exec_cmd(self, command: DebugCommand) -> Result:
            self.logger.info(f"Executing debug command: {command.cmd}")
            return Result(stdout="Debug executed", returncode=0)

3. Ensure the Executor Handles the New Command
==============================================
 
The ``ExecutorFactory`` class manages and creates executor instances based on command types.  
It maintains a registry (``_executors``) that maps command type strings to executor classes, allowing for dynamic execution of different command types.
Executors are registered using the ``register_executor`` method, which provides a decorator to associate a command type with a class.  
When a command is executed, the ``create_executor`` method retrieves the corresponding executor class, filters the constructor arguments based on the class's signature, and then creates an instance.

Accordingly, executors must be registered using the ``@executor_factory.register_executor('<command_type>')`` decorator. 

If the new executor class requires additional initialization arguments, these must be added to the ``_get_executor_config`` method in ``attackmate.py``. 
All configurations are always passed to the ``ExecutorFactory``.  
The factory filters the provided configurations based on the class constructor signature, ensuring that only the required parameters are used.

::

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


4. Modify the Loop Command to Include the New Command
=====================================================

Update the ``LoopCommand`` schema to include the new command.

::

    Command = Union[
            ShellCommand,
            DebugCommand,  # Newly added command
            # ... other command classes ...
        ]
    

5. Modify playbook.py to Include the New Command
=====================================================

Update the ``Playbook`` schema to include the new command.

::

    Commands = List[
        Union[
            ShellCommand,
            DebugCommand,  # Newly added command
            # ... other command classes ...
        ]
    ]

Once these steps are completed, the new command will be fully integrated into AttackMate and available for execution.

6. Add Documentation
=====================

Finally, update the documentation in `docs/source/playbook/commands` to include the new command.




      


