.. _integration:

=========================================
Using AttackMate in a Python Script
=========================================

AttackMate can be embedded in Python scripts for automation and custom attack scenarios.
Commands are created programmatically, dispatched one at a time, or run as a full playbook.

.. note::
   This feature is under development and the API may change. Bug reports are welcome.

Installation
============

Install AttackMate with `uv` or `pip` before importing it::

    uv add attackmate
    # or
    pip install attackmate

Quick Start
===========

``AttackMate.run_command`` is a coroutine, so all usage must be inside an ``async`` context::

    import asyncio
    from attackmate.attackmate import AttackMate
    from attackmate.command import Command

    async def main():
        attackmate = AttackMate()
        command = Command.create(type="shell", cmd="whoami")
        result = await attackmate.run_command(command)
        print(result)

    asyncio.run(main())

API Reference
=============

AttackMate
----------

.. code-block:: text

    class attackmate.attackmate.AttackMate(
        playbook=None,
        config=None,
        varstore=None,
        is_api_instance=False
    )

The central orchestration class. Instantiate it once per script; executors are
created lazily on first use and reused across calls.

**Constructor parameters**

.. list-table::
   :widths: 20 15 65
   :header-rows: 1

   * - Parameter
     - Type
     - Description
   * - ``playbook``
     - ``Playbook | None``
     - A parsed :class:`Playbook` object. Defaults to an empty playbook.
       Required when using :meth:`main` to execute a full sequence.
   * - ``config``
     - ``Config | None``
     - Tool configuration (Metasploit, Sliver, etc.). Defaults to safe
       defaults (see :ref:`config-class`).
   * - ``varstore``
     - ``dict | None``
     - Initial variables as a plain dictionary, e.g. ``{"HOST": "10.0.0.1"}``.
       If omitted, variables are read from the playbook ``vars`` section.
   * - ``is_api_instance``
     - ``bool``
     - Set to ``True`` when AttackMate is used as an embedded library rather
       than a CLI process. Defaults to ``False``.

**Methods**

``await attackmate.run_command(command) -> Result``
    Execute a single command and return its :class:`Result`.
    ``sftp`` commands are internally routed to the ``ssh`` executor.
    Returns ``Result(None, None)`` if no executor is registered for the type.

    Commands running in :ref:`background` mode return
    ``Result('Command started in background', 0)`` immediately.

``await attackmate.main() -> int``
    Execute all commands in the playbook, then clean up all open sessions and
    background processes. Handles ``KeyboardInterrupt`` gracefully.
    Returns ``0`` on completion.

``await attackmate.clean_session_stores()``
    Tear down all open sessions (Metasploit, SSH, VNC, Sliver, Remote) without
    running the playbook. Call this for manual cleanup after using
    ``run_command``.

Command
-------

.. code-block:: text

    class attackmate.command.Command

Factory interface for creating command instances. Do not instantiate directly;
use the static factory method.

``Command.create(type, cmd=None, **kwargs)``
    Look up the registered command class for ``type`` (and optionally ``cmd``),
    then instantiate it with the remaining keyword arguments.

    :param type: Command type string. See :ref:`command-types` below.
    :param cmd: The command string passed to the executor (required for most
        commands). For ``sliver`` and ``sliver-session``, ``cmd`` also
        selects the sub-command class.
    :param kwargs: Additional fields defined on the command schema
        (e.g. ``seconds``, ``varstore``, ``background``).
    :raises ValueError: If no class is registered for ``type`` / ``cmd``.

.. _command-types:

Available Command Types
^^^^^^^^^^^^^^^^^^^^^^^

Pass the string below as the ``type`` argument to ``Command.create()``.

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Type string
     - Description
   * - ``"shell"``
     - Execute a local shell command.
   * - ``"ssh"``
     - Execute a command over SSH.
   * - ``"sftp"``
     - Upload or download files over SFTP (routed to the SSH executor).
   * - ``"sleep"``
     - Pause execution for a number of seconds (``seconds`` kwarg).
   * - ``"debug"``
     - Print a value or variable to the log without side effects.
   * - ``"setvar"``
     - Set a variable in the variable store (``variable`` kwarg).
   * - ``"regex"``
     - Match a regex against a previous result and capture groups.
   * - ``"json"``
     - Parse a JSON string from a previous result and extract a value.
   * - ``"include"``
     - Load and execute commands from another playbook file.
   * - ``"loop"``
     - Repeat a nested list of commands until a condition is met.
   * - ``"mktemp"``
     - Create a temporary file or directory.
   * - ``"father"``
     - Execute commands as the parent/owning process.
   * - ``"webserv"``
     - Start a local HTTP server to serve files.
   * - ``"http-client"``
     - Send an HTTP request and capture the response.
   * - ``"browser"``
     - Automate a browser action via Playwright.
   * - ``"vnc"``
     - Interact with a VNC session.
   * - ``"remote"``
     - Delegate command execution to a remote AttackMate instance.
   * - ``"msf-module"``
     - Run a Metasploit module.
   * - ``"msf-session"``
     - Run a command inside an active Metasploit session.
   * - ``"msf-payload"``
     - Generate a Metasploit payload.
   * - ``"sliver"``
     - Manage a Sliver C2 server (``cmd``: ``"start_https_listener"``,
       ``"generate_implant"``).
   * - ``"sliver-session"``
     - Run a command inside a Sliver session (``cmd``: ``"execute"``,
       ``"cd"``, ``"ls"``, ``"mkdir"``, ``"download"``, ``"upload"``,
       ``"netstat"``, ``"ps"``, ``"pwd"``, ``"ifconfig"``,
       ``"process_dump"``, ``"rm"``, ``"terminate"``).

All command types also accept the base fields inherited from ``BaseCommand``:

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``background``
     - ``bool``
     - Run the command in the background. Defaults to ``False``.
   * - ``kill_on_exit``
     - ``bool``
     - Kill a background process when the playbook ends. Defaults to ``True``.
   * - ``only_if``
     - ``str | None``
     - Shell condition; command is skipped if this returns non-zero.
   * - ``error_if``
     - ``str | None``
     - Shell condition; execution aborts if this returns zero.
   * - ``error_if_not``
     - ``str | None``
     - Shell condition; execution aborts if this returns non-zero.
   * - ``loop_if``
     - ``str | None``
     - Shell condition; re-run the command while this returns zero.
   * - ``loop_if_not``
     - ``str | None``
     - Shell condition; re-run the command while this returns non-zero.
   * - ``loop_count``
     - ``str | int``
     - Maximum loop iterations. Defaults to ``3``.
   * - ``exit_on_error``
     - ``bool``
     - Abort the playbook if this command fails. Defaults to ``True``.
   * - ``save``
     - ``str | None``
     - Variable name to store the command's ``stdout`` in.

.. _config-class:

Config
------

.. code-block:: text

    class attackmate.schemas.config.Config

Top-level configuration object. All fields have safe defaults, so an empty
``Config()`` is valid for scripts that do not use Metasploit or Sliver.

.. list-table::
   :widths: 25 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``cmd_config``
     - ``CommandConfig``
     - Global command execution settings. See below.
   * - ``msf_config``
     - ``dict[str, MsfConfig]``
     - Named Metasploit RPC connections. See below.
   * - ``sliver_config``
     - ``dict[str, SliverConfig]``
     - Named Sliver C2 connections. See below.
   * - ``bettercap_config``
     - ``dict[str, BettercapConfig]``
     - Named Bettercap instances. Keys are referenced by ``webserv`` commands.
   * - ``remote_config``
     - ``dict[str, RemoteConfig]``
     - Named remote AttackMate instances.

**CommandConfig**

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``loop_sleep``
     - ``int``
     - Seconds to wait between loop iterations. Defaults to ``5``.
   * - ``command_delay``
     - ``float``
     - Seconds to wait before each command (excluding ``sleep``, ``debug``,
       ``setvar``). Defaults to ``0``.

**MsfConfig**

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``password``
     - ``str | None``
     - Metasploit RPC password.
   * - ``ssl``
     - ``bool``
     - Use SSL for the RPC connection. Defaults to ``True``.
   * - ``port``
     - ``int``
     - Metasploit RPC port. Defaults to ``55553``.
   * - ``server``
     - ``str``
     - Metasploit server address. Defaults to ``"127.0.0.1"``.
   * - ``uri``
     - ``str``
     - Metasploit RPC URI. Defaults to ``"/api/"``.

**SliverConfig**

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``config_file``
     - ``str | None``
     - Path to the Sliver client configuration file.

**BettercapConfig / RemoteConfig**

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``url``
     - ``str``
     - Base URL of the service.
   * - ``username``
     - ``str | None``
     - Authentication username.
   * - ``password``
     - ``str | None``
     - Authentication password.
   * - ``cafile``
     - ``str | None``
     - Path to a CA certificate file for TLS verification.

Result
------

.. code-block:: text

    class attackmate.result.Result(stdout, returncode)

Returned by ``run_command``.

.. list-table::
   :widths: 20 15 65
   :header-rows: 1

   * - Attribute
     - Type
     - Description
   * - ``stdout``
     - ``str``
     - The standard output of the command.
   * - ``returncode``
     - ``int``
     - ``0`` on success, non-zero on failure.

.. note::
   Commands running in :ref:`background` mode return
   ``Result('Command started in background', 0)`` immediately.

VariableStore
-------------

.. code-block:: text

    class attackmate.variablestore.VariableStore

Stores and resolves ``$variable`` references. When you pass a plain dictionary
to ``AttackMate(varstore=...)`` it is loaded into a ``VariableStore`` automatically,
so direct use of this class is optional. Access it as ``attackmate.varstore`` to
read or update variables at runtime.

**Methods**

``store.set_variable(variable, value)``
    Store a scalar string or a list. The ``$`` prefix in ``variable`` is stripped
    automatically. Integers are coerced to ``str``.

``store.get_variable(variable) -> str | list[str]``
    Retrieve a variable by name (without ``$`` prefix).
    Raises ``VariableNotFound`` if the variable does not exist.

``store.substitute_str(template_str, blank=False) -> str``
    Replace all ``$variable`` and ``$list[n]`` references in ``template_str``.
    If ``blank=True``, unresolved references are replaced with ``''``.

``store.from_dict(variables)``
    Bulk-load variables from a dictionary.

``store.replace_with_prefixed_env_vars()``
    Override stored variables with matching ``ATTACKMATE_<name>`` environment
    variables. Called automatically during ``AttackMate.__init__``.

Playbook
--------

.. code-block:: text

    class attackmate.schemas.playbook.Playbook(commands, vars=None)

A Pydantic model representing a full playbook. Use it when you want to execute
a sequence of pre-built commands via :meth:`AttackMate.main`, or when loading
from a YAML file (see :ref:`loading-from-yaml`).

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``commands``
     - ``list[Command]``
     - Ordered list of commands to execute.
   * - ``vars``
     - ``dict | None``
     - Initial variables for the variable store.


Usage Examples
==============

Running a Single Command
------------------------

::

    import asyncio
    from attackmate.attackmate import AttackMate
    from attackmate.command import Command
    from attackmate.schemas.config import Config
    from attackmate.logging_setup import initialize_logger

    async def main():
        initialize_logger(debug=False, append_logs=False)

        config = Config(
            msf_config={"default": {"password": "your_password", "ssl": True, "port": 55553}},
            cmd_config={"loop_sleep": 10},
        )
        varstore = {"HOST": "10.0.0.1"}

        attackmate = AttackMate(config=config, varstore=varstore, is_api_instance=True)

        command = Command.create(type="shell", cmd="echo $HOST")
        result = await attackmate.run_command(command)

        print("Output:", result.stdout)
        print("Return code:", result.returncode)

        await attackmate.clean_session_stores()

    asyncio.run(main())

Running Multiple Commands
-------------------------

::

    import asyncio
    from attackmate.attackmate import AttackMate
    from attackmate.command import Command

    async def main():
        am = AttackMate(is_api_instance=True)

        cmd1 = Command.create(type="sleep", cmd="sleep", seconds="1")
        cmd2 = Command.create(type="debug", cmd="hello world")
        cmd3 = Command.create(type="shell", cmd="id", save="RESULT")
        cmd4 = Command.create(type="debug", cmd="$RESULT")

        for cmd in [cmd1, cmd2, cmd3, cmd4]:
            result = await am.run_command(cmd)
            if result.returncode != 0:
                print(f"Command failed: {result.stdout}")
                break

        await am.clean_session_stores()

    asyncio.run(main())

.. _loading-from-yaml:

Running a Playbook from a YAML File
------------------------------------

Use ``parse_playbook`` and ``parse_config`` from ``attackmate.playbook_parser``
to load a playbook file and optional config file, then pass them to
``AttackMate.main``::

    import asyncio
    import logging
    from attackmate.attackmate import AttackMate
    from attackmate.playbook_parser import parse_playbook, parse_config
    from attackmate.logging_setup import initialize_logger

    async def main():
        logger = initialize_logger(debug=False, append_logs=False)
        config = parse_config(None, logger)          # reads ~/.config/attackmate.yml
        playbook = parse_playbook("my_playbook.yml", logger)

        am = AttackMate(playbook=playbook, config=config)
        await am.main()

    asyncio.run(main())

Updating Variables at Runtime
------------------------------

Access ``attackmate.varstore`` directly to read or write variables between
commands::

    import asyncio
    from attackmate.attackmate import AttackMate
    from attackmate.command import Command

    async def main():
        am = AttackMate(varstore={"TARGET": "192.168.1.1"})

        am.varstore.set_variable("PORT", "8080")

        result = await am.run_command(
            Command.create(type="shell", cmd="curl http://$TARGET:$PORT")
        )
        print(result.stdout)

        host = am.varstore.get_variable("TARGET")
        print("Target was:", host)

    asyncio.run(main())

Checking Results
----------------

::

    result = await am.run_command(command)

    if result.returncode == 0:
        print("Success:", result.stdout)
    else:
        print("Failed with code:", result.returncode)

Environment Variable Overrides
==============================

Any variable in the store can be overridden at runtime by setting an environment
variable with the ``ATTACKMATE_`` prefix::

    export ATTACKMATE_HOST=10.0.0.2

This overrides the variable ``HOST`` regardless of the value set via ``varstore``
or the playbook ``vars`` section. Overrides are applied automatically during
``AttackMate.__init__``.
