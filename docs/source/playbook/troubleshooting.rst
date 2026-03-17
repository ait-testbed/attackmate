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

.. _error-commands-not-a-list:

Commands Not Formatted as a List
---------------------------------

**Symptom**

.. code-block:: text

    ERROR | A Validation error occured when parsing playbook file playbooks/example.yml
    ERROR | Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Playbook
    commands
      Input should be a valid list [type=list_type, input_value={'type': 'shell',
      'cmd': 'whoami'}, input_type=dict]

**Cause**

The ``commands`` field in the playbook is not formatted as a YAML list.
A command was defined as a plain mapping instead of a list entry.

**Solution**

Each command must be a list item, prefixed with ``-``:

.. code-block:: yaml

    # Wrong — commands is a plain mapping:
    commands:
      type: shell
      cmd: whoami

    # Correct — commands is a list:
    commands:
      - type: shell
        cmd: whoami

.. seealso::
    See * :ref:`Basic Usage <basic-usage>` for the full playbook structure.

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

Remote Command Execution Errors
===============================

.. _error-remote-connection-not-found:

Remote Connection Not Found in Config
--------------------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing REMOTE AttackMate command: Type='remote', RemoteCmd='execute_command' on server attackmate_server
    ERROR | Execution failed: Remote connection 'attackmate_server' not found in config.
    ...
    attackmate.execexception.ExecException: Remote connection 'attackmate_server' not found in config.
    ERROR | Error: Remote connection 'attackmate_server' not found in config.

**Cause**

A ``remote`` command references a connection name (here ``attackmate_server``)
that has no corresponding entry in the ``remote_config`` section of the
configuration file.

**Solution**

* Ensure the connection name used in the playbook command matches an entry
  defined in ``remote_config`` in your configuration file.
* Check for typos in the connection name - it is case-sensitive.

.. code-block:: yaml

    # In your config file — define the connection:
    remote_config:
      attackmate_server:
        url: https://theremoteserver:8445
        username: testuser
        password: testuser
        cafile: /path/to/cert.pem

    # In your playbook — reference the same name:
    commands:
      - type: remote
        cmd: execute_command
        connection: attackmate_server
        remote_command:
            type: shell
            cmd: whoami

.. seealso::
    :ref:`remote_config` for the full list of required configuration fields.

----

.. _error-remote-authentication-failed:

Remote Authentication Failed
-----------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing REMOTE AttackMate command: Type='remote', RemoteCmd='execute_command' on server attackmate_server (https://localhost:8445)
    INFO  | Client will verify https://localhost:8445 SSL using CA: /path/to/cert.pem
    INFO  | Successfully created remote client for: attackmate_server
    INFO  | Attempting login to https://localhost:8445/login for user 'admin'...
    ERROR | Login failed for 'admin' at https://localhost:8445: 401 - {"detail":"Incorrect username or password"}
    ERROR | Authentication failed or credentials not provided for https://localhost:8445


**Cause**

The credentials provided in the configuration do not match those expected
by the remote AttackMate server. The server returned a ``401 Unauthorized``
response.

**Solution**

* Check that the ``username`` and ``password`` in your ``remote_config``
  entry are correct.
* Verify that the user account exists on the remote AttackMate server and
  that the password has not changed.


.. seealso::
    :ref:`remote` and :ref:`remote_config` for the full list of required configuration fields.

----

.. _error-remote-ssl-cert-not-found:

Remote SSL Certificate Not Found
----------------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing REMOTE AttackMate command: Type='remote', RemoteCmd='execute_command' on server attackmate_server (https://localhost:8445)
    ERROR | CA certificate file not found: /path/to/certificate.pem. Falling back to default verification.
    INFO  | Successfully created remote client for: attackmate_server
    INFO  | Attempting login to https://localhost:8445/login for user 'testuser'...
    ERROR | Login request to https://localhost:8445 failed: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate (_ssl.c:1010)
    ...
    httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate (_ssl.c:1010)
    ERROR | Authentication failed or credentials not provided for https://localhost:8445


**Cause**

The CA certificate file specified in ``remote_config`` could not be found at
the given path. AttackMate fell back to default SSL verification, which then
failed because the remote server uses a self-signed certificate.

**Solution**

* Check that the ``cafile`` path in your ``remote_config`` points to the
  correct certificate file and that the file exists.
* Ensure the path is absolute or correctly relative to the working directory
  from which AttackMate is invoked.

.. code-block:: yaml

    remote_config:
      attackmate_server:
        url: https://theremoteserver:8445
        username: testuser
        password: testuser
        cafile: /path/to/cert.pem
.. seealso::
    :ref:`remote` and :ref:`remote_config` for the full list of required configuration fields.


----

.. _error-remote-ssl-cert-invalid:

Remote SSL Certificate Invalid
--------------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing REMOTE AttackMate command: Type='remote', RemoteCmd='execute_command' on server attackmate_server (https://localhost:8445)
    INFO  | Client will verify https://localhost:8445 SSL using CA: /path/to/wrong.pem
    INFO  | Successfully created remote client for: attackmate_server
    INFO  | Attempting login to https://localhost:8445/login for user 'testuser'...
    ERROR | Login request to https://localhost:8445 failed: [X509] PEM lib (_ssl.c:4106)

**Cause**

The CA certificate file specified in ``remote_config`` was found and loaded,
but its contents are not valid for verifying the remote server's certificate.
This happens when the ``cafile`` points to the wrong certificate — for example
a certificate from a different CA or an unrelated server.

**Solution**

* Ensure that the ``cafile`` in your ``remote_config`` points to the correct
  CA certificate that was used to sign the remote AttackMate server's
  certificate.
* If you are unsure which certificate to use, check the server setup
  documentation or regenerate the certificate and update both the server
  and the ``cafile`` path accordingly.

.. code-block:: yaml

    remote_config:
      attackmate_server:
        url: https://localhost:8445
        username: testuser
        password: testuser
        cafile: /path/to/correct-ca.pem   # must match the server's CA

.. seealso::

    :ref:`remote` and :ref:`remote_config` for the full list of required
    configuration fields.
``

----

.. _error-remote-command-not-supported:

Command Type Not Supported on Remote Instances
------------------------------------------------------

**Symptom**

.. code-block:: text

    ERROR | A Validation error occured when parsing playbook file playbooks/remote_remote.yml
    ERROR | Traceback (most recent call last):
      ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Playbook
    commands.0.remote.remote_command
      Input tag 'remote' found using 'type' does not match any of the expected tags:
      'sliver-session', 'sliver', 'browser', 'shell', 'msf-module', 'msf-session',
      'msf-payload', 'sleep', 'ssh', 'father', 'sftp', 'debug', 'setvar', 'regex',
      'mktemp', 'include', 'loop', 'webserv', 'http-client', 'json', 'vnc', 'bettercap'
      [type=union_tag_invalid, input_value={'type': 'remote', 'cmd':...'path/to/playbook'}, input_type=dict]

**Cause**

A ``remote`` command was used as the ``remote_command`` of another ``remote``
command - that is, a remote command was nested inside another remote command.
This is not supported; a remote AttackMate instance cannot itself dispatch
further remote commands.

.. code-block:: yaml

    # Wrong — remote cannot be used as a remote_command:
    commands:
      - type: remote
        cmd: execute_command
        connection: attackmate_server
        remote_command:
          type: remote
          cmd: execute_playbook
          connection: another_server
          playbook_path:

**Solution**

* Remove the nesting — a ``remote`` command can only wrap command types that
  are executable on the target AttackMate instance directly.
* If you tried to execute a RemotelyExecutableCommand on the remote instance check for spelling mistakes in the ``type`` field


----

.. _error-remote-playbook-invalid:

Invalid Playbook Submitted to Remote Instance (422 Server Error)
----------------------------------------------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing REMOTE AttackMate command: Type='remote', RemoteCmd='execute_playbook' on server attackmate_server (https://localhost:8445)
    INFO  | Login successful for 'testuser' at https://localhost:8445. Token stored.
    ERROR | API Error (POST https://localhost:8445/playbooks/execute/yaml): 422
    ERROR | Server Detail: {'message': 'Invalid playbook: 1 validation error(s).', 'errors': ["'commands': Input should be a valid list"]}

**Cause**

The playbook submitted to the remote AttackMate instance failed validation
on the server side. Authentication succeeded, but the server rejected the
playbook with a ``422 Unprocessable Entity`` response. The server returns
a ``422`` in three cases:

* **YAML parse error** — the playbook file is not valid YAML. The error
  message will read ``Invalid playbook YAML: failed to parse YAML.``
* **Validation error** — the playbook is valid YAML but fails Pydantic
  model validation, for example a missing required field or an invalid
  command type. The error message will read
  ``Invalid playbook: N validation error(s).``
* **Value error** — the playbook contains a semantic error that cannot be
  caught by schema validation alone. The error message will read
  ``Invalid playbook YAML.``

In the example above the ``commands`` field is not a valid list — the same
underlying issue described in :ref:`error-commands-not-a-list`, but caught
by the remote instance rather than locally.

**Solution**

* Inspect the ``errors`` field in the server detail for the specific
  validation message.
* Validate the playbook locally first by running it directly with AttackMate
  before submitting it to a remote instance — local validation produces more
  detailed error output:

.. code-block:: bash

    $ uv run attackmate playbooks/whoami.yml

* For YAML syntax errors, check the playbook file for incorrect indentation,
  missing colons, or unquoted special characters.
* For validation errors, refer to the playbook schema

.. seealso::
    :ref:`error-commands-not-a-list` for the command not a valid list validation error.

    :ref:`error-invalid-command-type` for invalid command type errors.

    :ref:`error-missing-field` for missing required field errors.

    :ref:`remote` for documentation on the ``execute_playbook`` command.

----


SSH Command Errors
==================

.. _error-ssh-no-session:

No Existing SSH Session
-----------------------

**Symptom**

.. code-block:: text

  INFO     | Executing SSH-Command: 'id'
  ERROR    | No existing session

**Cause**

An ``ssh`` command was executed, but AttackMate could not find an active session for the target host. This typically happens when:
* The user specified in the playbook does not exist on the remote target.


**Solution**

* Verify User Existence: Ensure the ``user`` specified in your playbook actually exists on the target machine.

.. seealso::
    :ref:`ssh` for details on how ssh sessions are used within AttackMate.

----

.. _error-unable-to-connect-session:

Unable to connect SSH Session
-----------------------

**Symptom**

.. code-block:: text

  INFO     | Executing SSH-Command: 'id'
  ERROR    | [Errno None] Unable to connect to port 22 on 10.110.0.17

**Cause**

An ``ssh`` command was executed, but AttackMate could not establish a TCP
connection to the specified port on the target host. This typically means
one of the following:

* The target host is unreachable (e.g. routing issue, host is down).
* The SSH service is not running or is listening on a different port.
* A firewall or network policy is blocking the connection.
* The IP address or port in the SSH configuration is incorrect.

**Solution**
* Verify that the target host is reachable, for example with ``ping`` or
  ``traceroute``.
* Confirm that an SSH service is running on the target and listening on the
  configured port (default: ``22``).
* Check that no firewall rule is blocking the connection on either the
  client or the target side.
* Review the ``host`` and ``port`` fields in your SSH configuration and
  ensure they match the target.
* Check Credentials: If you are using password or key-based authentication,
  verify that the credentials in your configuration/playbook are valid for that remote user.

.. seealso::
    :ref:`ssh` for details on how ssh sessions are used within AttackMate.

----

.. _error-ssh-session-not-in-store:

SSH Session Not Found in Session Store
---------------------------------------

**Symptom**

.. code-block:: text

    INFO  | Executing SSH-Command: 'id'
    ERROR | SSH-Session not in Session-Store: example-session

**Cause**

An ``ssh`` command references a named session that does not exist in
AttackMate's session store. This happens when the ``session`` field in
the command points to a session that was never established — either
because the session-opening command was never executed, was skipped due
to a prior error, or the session name contains a typo.

**Solution**
* Review the playbook order and confirm the session is established before
  it is used.
* Ensure that a session-opening SSH command with the matching session name
  runs successfully before any commands that reference it.
* Check for typos in the ``session`` field — session names are case-sensitive.

.. code-block:: yaml

    # Wrong — session name does not match the created session:
    commands:
      - type: ssh
        cmd: id
        username: user
        key_filename: /home/user/.ssh/key
        hostname: 10.0.0.1
        creates_session: "foothold"
      - type: ssh
        cmd: id
        session: "typo-session"   # does not match "foothold"

    # Correct — session name matches exactly:
    commands:
      - type: ssh
        cmd: id
        username: user
        key_filename: /home/user/.ssh/key
        hostname: 10.0.0.1
        creates_session: "foothold"
      - type: ssh
        cmd: id
        session: "foothold"


.. seealso::
    :ref:`ssh` for details on how SSH sessions are created and referenced
    within AttackMate.

----

Webserv Command Errors
======================

.. _error-webserv-hangs:

Playbook Hangs After webserv Command
--------------------------------------

**Symptom**

The playbook stops progressing and hangs indefinitely after a ``webserv``
command. No subsequent commands are executed.

.. code-block:: text

  2026-03-16 16:22:19 INFO     | Delay before commands: 1.0 seconds
  2026-03-16 16:22:20 INFO     | Serving /home/user/files/example.txt via HTTP on Port 8000

**Cause**

The ``webserv`` command starts an HTTP file server and blocks execution
until the server is stopped. Without setting ``background: true``, AttackMate
waits for the server to finish before continuing, which causes the playbook
to hang indefinitely.

**Solution**

* Always set ``background: true`` on ``webserv`` commands so that the server
  is started in the background and playbook execution continues immediately.

.. code-block:: yaml

    # Wrong — webserv blocks playbook execution:
    commands:
      - type: webserv
        local_path: /home/user/files/example.txt
        port: 8000

    # Correct — webserv runs in the background:
    commands:
      - type: webserv
        local_path: /home/user/files/example.txt
        port: 8000
        background: true

.. seealso::
    :ref:`webserv` for the full list of available configuration fields.
