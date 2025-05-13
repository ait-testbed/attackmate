Adding a New Executor
=====================
.. _base_executor:

================
Base Executor
================

The ``BaseExecutor`` is the core class from which all executors in AttackMate inherit.
It provides a structured approach to implementing custom executors.

Key Features
------------

- **Command Execution Handling**: Defines the execution flow for commands, including logging, metadata processing, and error handling.
- **Variable Substitution**: Supports dynamic replacement of variables in command execution using ``CmdVars``.
- **Looping & Conditional Execution**: Implements logic to repeat commands or execute them based on conditions.
- **Background Execution**: Allows certain commands to run asynchronously.
- **Error Handling**: Supports stopping execution on errors via ``ExitOnError``.
- **Logging & Output Management**: Tracks execution details, metadata, and output results.

Execution Flow
--------------

1. **Command Logging**: Logs execution details, metadata, and JSON-formatted information.
2. **Command Processing**: Substitutes variables, applies looping logic, and checks execution conditions.
3. **Execution and Result Handling**: Calls ``_exec_cmd()``, processes results, and manages errors.
4. **Output Saving**: If specified, saves command output to a file.

Implementing a Custom Executor
-------------------------------

To create a custom executor, inherit from ``BaseExecutor`` and implement the ``_exec_cmd()`` method. Other methods can be overriden as needed.

Example:

.. code-block:: python

    from attackmate.executors.base_executor import BaseExecutor
    from attackmate.result import Result

    class CustomExecutor(BaseExecutor):
        def _exec_cmd(self, command) -> Result:
            self.logger.info(f"Executing custom command: {command.cmd}")
            return Result(stdout="Execution complete", returncode=0)

Constructor
------------

.. code-block:: python

    def __init__(
        self, pm: ProcessManager, varstore: VariableStore, cmdconfig=CommandConfig(), substitute_cmd_vars=True
    ):

- ``pm``: Instance of ``ProcessManager`` to handle process execution.
- ``varstore``: Instance of ``VariableStore`` to manage variables.
- ``cmdconfig``: Optional configuration settings for command execution.
- ``substitute_cmd_vars``: Enables variable substitution in command strings, defaults to ``True``.


Overridable Methods
--------------------

The following methods can be overridden in custom executors to modify behavior:

**Command Execution**

.. code-block:: python

    def _exec_cmd(self, command: BaseCommand) -> Result:
        return Result(None, None)

This is the core execution function and must be implemented in subclasses.
It should return a ``Result`` object containing the execution outcome.

.. note::

    The ``_exec_cmd()`` method **must** be implemented in any subclass of ``BaseExecutor``.
    This method defines the core execution logic for the command and is responsible for returning a ``Result`` object.


**Logging Functions**

The methods ``log_command``, ``log_matadata`` and ``log_json`` log command execution details and can be overridden for custom logging formats.

**Command Execution Flow**

The ``run()`` method defines the high-level execution flow of a command.
It includes condition checking, logging, and calling the actual execution logic.

**Output Handling**

The ``save_output()`` function manages saving output to a file. It can be overridden to implement alternative storage methods.


executor __init__.py
--------------------
.. note::

    Add the new executor to the ``__all__`` list in the ``__init__.py`` file of the ``attackmate.executors`` module.
