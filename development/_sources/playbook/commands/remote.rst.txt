======
remote
======

Execute playbooks or commands on a remote AttackMate instance.
Remote connections are defined in the ``remote_config`` section of the configuration file.
If no ``connection`` is specified, the first entry in the ``remote_config`` section is used as default.

.. warning::

   Options such as ``background`` and ``only_if`` defined on the ``remote`` command apply
   to the **local** execution context, not to the command or playbook running on the remote
   instance.

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

   The operation to perform on the remote instance. One of:

   - ``execute_command`` — Execute a single AttackMate command on the remote instance.
     Requires ``remote_command``
   - ``execute_playbook`` — Execute a full playbook YAML file on the remote instance.
     Requires ``playbook_path``

   :type: str (``execute_command`` | ``execute_playbook``)
   :required: True

.. confval:: connection

   Name of the remote connection to use, as defined in the ``remote_config`` section
   of the AttackMate configuration file. If omitted, the first entry in ``remote_config`` is used.

   :type: str
   :default: first entry in ``remote_config``
   :required: False

.. confval:: playbook_path

   Path to a local YAML playbook file to sent to and execute on the remote AttackMate.
   Required when ``cmd`` is ``execute_playbook``.

   :type: str
   :required: when ``cmd: execute_playbook``

.. confval:: remote_command

   An inline AttackMate command to execute on the remote instance.
   Supports any command type that the remote AttackMate instance is configured to handle
   (e.g., ``type: shell``, ``type: sliver``, etc., EXCEPT ``type: remote``  itself). Required when ``cmd`` is ``execute_command``.

   :type: RemotelyExecutableCommand
   :required: when ``cmd: execute_command``


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

Execute a playbook on the default remote connection
---------------------------------------------------

.. code-block:: yaml

   commands:
     - type: remote
       cmd: execute_playbook
       playbook_path: /homeuser/playbooks/recon.yaml
