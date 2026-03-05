======
remote
======

This command executes playbooks or commands on a remote AttackMate instance.
The connection to the remote instance is defined in the ``remote_config`` section of the configuration file.
If no connection is specified, the first entry in the ``remote_config`` section will be used as default.

Configuration
=============

Remote connections are defined under the ``remote_config`` key in the AttackMate configuration file.
Each entry requires at minimum a ``url`` a ``username``, ``password``, and ``cafile``
for TLS certificate verification.

.. code-block:: yaml

   remote_config:
     my-remote-instance:
       url: https://192.42.0.254:8443
       username: admin
       password: secret
       cafile: /path/to/ca.pem

Commands
========

Execute Command
---------------

Executes a single AttackMate command on the remote instance.

.. code-block:: yaml

   commands:
     - type: remote
       cmd: execute_command
       connection: my-remote-instance
       remote_command:
         type: shell
         cmd: whoami

Execute Playbook
----------------

Sends a local playbook YAML file to the remote instance and executes it there.

.. code-block:: yaml

   commands:
     - type: remote
       cmd: execute_playbook
       connection: my-remote-instance
       playbook_path: /path/to/playbook.yaml

Options
=======

.. confval:: cmd

   The remote operation to perform. Must be one of the following:

   - ``execute_command`` — Execute a single AttackMate command on the remote instance.
     Requires ``remote_command`` to be set.
   - ``execute_playbook`` — Execute a full playbook YAML file on the remote instance.
     Requires ``playbook_path`` to be set.

   :type: str (``execute_command`` | ``execute_playbook``)

.. confval:: connection

   The name of the remote connection to use, as defined in the ``remote_config`` section
   of the configuration file. If omitted, the first entry in ``remote_config`` is used
   as the default connection.

   :type: str
   :default: first entry in ``remote_config``

.. confval:: playbook_path

   Path to a local YAML playbook file that will be read and sent to the remote AttackMate
   instance for execution. Required when ``cmd`` is ``execute_playbook``.

   :type: str

.. confval:: remote_command

   An inline AttackMate command definition that will be executed on the remote instance.
   This supports any command type that the remote AttackMate instance is configured to handle
   (e.g., ``shell``, ``sliver``, etc., EXCEPT another remote_command). Required when ``cmd`` is ``execute_command``.

   :type: RemotelyExecutableCommand

.. warning::

   Parameters such as ``background`` and ``only_if`` defined at the top-level ``remote`` command
   apply to the **local** execution of the remote command, not to the command executed on the
   remote instance.

Examples
========

Execute a shell command on a remote instance
--------------------------------------------

.. code-block:: yaml

   vars:
     $REMOTE_HOST: my-remote-instance

   commands:
     - type: remote
       cmd: execute_command
       connection: $REMOTE_HOST
       remote_command:
         type: shell
         cmd: id

Execute a playbook on a remote instance using the default connection
--------------------------------------------------------------------

.. code-block:: yaml

   commands:
     - type: remote
       cmd: execute_playbook
       playbook_path: /homeuser/playbooks/recon.yaml
