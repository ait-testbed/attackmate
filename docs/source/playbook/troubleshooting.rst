.. _troubleshooting:

===============
Troubleshooting
===============

This page lists common error messages and their solutions.

.. _error-validation:

Playbook Validation Errors
==========================

These errors occur when AttackMate cannot parse the playbook file.
They are reported as ``ValidationError`` and originate from Pydantic's
model validation.

----

.. _error-invalid-command-type:

Invalid Command Type
--------------------

**Symptom**

.. code-block:: text

    ERROR | A Validation error occured when parsing playbook file playbooks/example.yml
    ERROR | Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Playbook
    commands.0
      Input tag 'shel' found using 'type' does not match any of the expected tags:
      'sliver-session', 'sliver', 'browser', 'shell', 'msf-module', 'msf-session',
      'msf-payload', 'sleep', 'ssh', 'father', 'sftp', 'debug', 'setvar', 'regex',
      'mktemp', 'include', 'loop', 'webserv', 'http-client', 'json', 'vnc',
      'bettercap', 'remote'
      [type=union_tag_invalid, input_value={'type': 'shel', 'cmd': 'whoami'}, input_type=dict]

**Cause**

The ``type`` field of a command does not match any registered command type.
In the example above, ``shel`` is a typo for ``shell``.

**Solution**

* Check the spelling of the ``type`` field in your playbook. Valid types are
  listed in the error message itself.
* If this is a new command type you are trying to implement, verify that it is correctly
  registered in the :class:`CommandRegistry` and included in the executor
  factory. see :ref:`Adding a new Command <command>`.

.. seealso::
    see :ref:`commands` for a full list of available command types.

----

.. _error-missing-field:

Missing Required Field
----------------------

**Symptom**

.. code-block:: text

    ERROR | A Validation error occured when parsing playbook file playbooks/example.yml
    ERROR | Missing field in shell command: cmd - Field required
    ERROR | Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Playbook
    commands.0.shell.cmd
      Field required [type=missing, input_value={'type': 'shell'}, input_type=dict]

**Cause**

A required field is missing from a command definition. In the example above,
the ``cmd`` field is missing from a ``shell`` command.

**Solution**

* Check the command definition in your playbook and ensure all required fields
  are present.
* Refer to the documentation for the specific command type to see which fields
  are required.

----

Sliver Command Execution Errors
===============================

These errors occor when there is a faulty sliver configuration, sliver is not installed etc.

.. _error-sliver-client-not-defined:

Sliver Client Not Defined
-------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing Sliver-command: 'start_https_listener'
    ERROR | Sliver execution failed: SliverClient is not defined
    ERROR | SliverClient is not defined

**Cause**

A Sliver command was executed but no ``SliverClient`` was defined.

**Solution**

* Verify that the ``sliver_config`` in your configuration points to a valid
  Sliver client configuration file and that sliver is installed.

.. seealso::
    :ref:`sliver` and :ref:`sliver_config` for setup instructions and required configuration fields.

----

.. _error-sliver-connection-refused:

Sliver Server Unreachable
-------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing Sliver-command: 'start_https_listener'
    ERROR | An error occurred: <AioRpcError of RPC that terminated with:
          status = StatusCode.UNAVAILABLE
          details = "failed to connect to all addresses; last error: UNKNOWN:
          ipv4:127.0.0.1:31337: Failed to connect to remote host: connect:
          Connection refused (111)"
          debug_error_string = "UNKNOWN:Error received from peer {grpc_status:14,
          grpc_message:"failed to connect to all addresses; last error: UNKNOWN:
          ipv4:127.0.0.1:31337: Failed to connect to remote host: connect:
          Connection refused (111)"}">

**Cause**

AttackMate could not establish a gRPC connection to the Sliver C2 server.
The server is either not running, not reachable at the configured address
and port, or is blocked by a firewall.

**Solution**

* Verify that the Sliver C2 server is running, the command to start it is ``sliver-server``,
  per default it listens on port ``31337``
* Check that the ``config_file`` in ``sliver_config`` points to the correct
  client configuration file and that the host and port match the running
  server (default: ``127.0.0.1:31337``).
* Ensure no firewall or network policy is blocking the connection.

.. seealso::
    :ref:`sliver` and :ref:`sliver_config` for setup instructions and required configuration fields.
