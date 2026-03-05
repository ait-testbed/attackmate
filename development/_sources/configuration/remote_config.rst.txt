.. _remote_config:

=============
remote_config
=============

The remote_config section defines connections to remote AttackMate instances. This allows one AttackMate instance to act as a controller, dispatching playbooks or commands to remote nodes.

Like other executors, the configuration uses unique identifiers (names) for each connection. If a command in a playbook does not explicitly specify a connection, the first entry defined in this configuration is used as the default.

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
   playbook_yaml_path: path/to/playbook.yml

.. confval:: url

The base URL of the remote AttackMate REST API.

:type: str :required: True

.. confval:: username

The username for authentication with the remote AttackMate instance.

:type: str :required: False

.. confval:: password

The password for authentication with the remote AttackMate instance.

:type: str :required: False

.. confval:: cafile

The path to a CA certificate file used to verify the remote server's SSL certificate. This is highly recommended when using HTTPS.

:type: str :required: False
