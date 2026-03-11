.. _remote_config:

=============
remote_config
=============

``remote_config`` defines connections to remote AttackMate instances. This allows one AttackMate instance to act as a controller, dispatching playbooks or commands to remote nodes.

Each connection is identified by a user-defined name that can be referenced in playbook
commands via the ``connection`` field. If no connection is specified, the first entry in
the configuration is used as the default.

.. code-block:: yaml

  remote_config:
    remote_server:
      url: "https://10.0.0.5:5000"
      username: admin
      password: securepassword
      cafile: "/path/to/cert.pem"
    another_server:
      url: "https://10.0.0.6:5000"
      username: user
      password: anotherpassword
      cafile: "/path/to/another_cert.pem"


The following example shows how to target a specific remote instance, and how the
default connection is used when none is specified:

.. code-block:: yaml

  commands:
    # Executed on 'another_server'
    - type: remote
      connection: another_server
      cmd: execute_command
      remote_command:
        type: shell
        cmd: "whoami"

    # Executed on 'remote_server' (defaults to first remote_config entry))
    - type: remote
      cmd: execute_playbook
      playbook_path: path/to/playbook.yml

.. confval:: url

The base URL of the remote AttackMate REST API.

:type: str
:required: True

.. confval:: username

The username for authentication with the remote AttackMate instance.

:type: str
:required: False

.. confval:: password

The password for authentication with the remote AttackMate instance.

:type: str
:required: False

.. confval:: cafile

The path to a CA certificate file used to verify the remote server's TLS certificate. Strongly recommended when connecting over HTTPS.

:type: str
:required: False
