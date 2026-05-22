.. _remote_api_intro:

==========
Remote API
==========

AttackMate can execute commands and playbooks on a remote AttackMate
instance. This is useful when the tools required by a playbook, such as
Metasploit, Sliver, browsers, or network access to a target environment, are
available on another host.

The remote setup uses two components:

* `attackmate-api-server <https://github.com/ait-testbed/attackmate-api-server>`__:
  runs on the remote AttackMate host and exposes an HTTPS API.
* `attackmate-client <https://github.com/ait-testbed/attackmate-client>`__:
  runs on the local/client host and sends commands or playbooks to the API
  server.

The `attackmate-ansible <https://github.com/ait-testbed/attackmate-ansible>`__
role can install and configure both sides.

Requirements
============

A working remote setup needs at least:

* AttackMate installed on the server.
* attackmate-api-server installed and running on the server.
* attackmate-client installed on the client.
* The server TLS certificate copied to the client.
* A valid ``remote_config`` entry on the client, or provided as cli argument to ``attackmate-client``.
* Any tools used by the remote playbook installed on the server, for example
  ``msfrpcd`` for Metasploit commands.

It is recommended to install AttackMate on the client too. This allows the
client to parse local wrapper playbooks and use the normal ``attackm8`` command.

Architecture
============

When a remote playbook uses ``cmd: execute_playbook``, the referenced
``playbook_path`` is read on the client machine. The client then sends the
playbook YAML content to the API server.

The commands inside that submitted playbook run on the server. Therefore paths
inside the submitted playbook, such as payload paths, temporary files, local
uploads, or tool configuration, are resolved on the server.

Sample Config
=============

Save this as ``/etc/attackmate.yml`` on the client:

.. code-block:: yaml

    msf_config:
      server: localhost
      password: hackerman

    cmd_config:
      command_delay: 2

    remote_config:
      attackmate-server:
        url: "https://10.0.0.5:8445"
        username: admin
        password: securepassword
        cafile: "/etc/ssl/certs/attackmate.pem"

The ``cafile`` must point to the certificate used by the API server. If the
certificate is missing or does not match the server, HTTPS verification will
fail.

First Run
=========

Create a small local wrapper playbook on the client:

.. code-block:: yaml

    commands:
      - type: remote
        cmd: execute_playbook
        connection: attackmate-server
        playbook_path: examples/remote_put.yml

Run it with:

.. code-block:: console

    uv run attackm8 --debug remote_wrapper.yml

The client should log in to the API server, send the referenced playbook, and
print the remote execution result.

Testing The API Server
======================

Check that the API service is reachable:

.. code-block:: console

    curl -k https://10.0.0.5:8445/

Metasploit
==========

If a playbook uses Metasploit commands, ``msfrpcd`` must be running on the
server and the AttackMate server configuration must match it.

Example:

.. code-block:: yaml

    msf_config:
      server: localhost
      port: 55553
      password: hackerman
      ssl: true

A common symptom of a wrong Metasploit configuration, or msfrpcd not running, is:

.. code-block:: text

    2026-05-20 11:01:37 INFO     | Login successful for 'admin' at https://192.168.0.30:8445. Token stored.
    2026-05-20 11:02:37 ERROR    | Request Error (POST https://192.168.0.30:8445/playbooks/execute/yaml): The read operation timed out


Troubleshooting
===============

``The read operation timed out``

The client waited longer than its configured HTTP timeout. This can happen when
the remote playbook is still running, waiting for a session, or stuck in a tool
such as Metasploit. Check the server logs and any AttackMate playbook logs.

You can also increase the timeout period of attackmate-client by changing DEFAULT_TIMEOUT in ``/usr/local/share/attackmate/.venv/lib/python3.12/site-packages/attackmate_client/attackmate_client.py``

Server Logs
===========

The systemd service logs are available with:

.. code-block:: console

    journalctl -u attackmate-api -f

If file logging is enabled for API playbook runs, inspect the configured log
directory, for example:

.. code-block:: console

    tail -f /var/log/attackmate-api/*_output.log
