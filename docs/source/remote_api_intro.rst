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

`attackmate-client` offers a CLI and a python library to execute commands and playbooks on a
remote AttackMate server. It is only required on the client when you want to use the Remote API
on an attackmate-api-server.

The `attackmate-ansible <https://github.com/ait-testbed/attackmate-ansible>`__
role can install and configure both sides.

Requirements
============

A working remote setup needs at least:

* AttackMate installed on the server.
* attackmate-api-server installed and running on the server.
* attackmate-client installed on the client, to access the remote API.
* The server TLS certificate copied to the client.
* A valid ``remote_config`` entry on the client, or provided as cli argument to ``attackmate-client``.
* Any tools used by the remote playbook installed on the server, for example
  ``msfrpcd`` for Metasploit commands.

If you installed ``Attackmate`` on the client, it is not recommended to install ``attackmate-client``, as it will
already have pulled that in as a dependency. 

You can install just the ``attackmate-client``, if all you want to do on the client is to send remote commands
and playbooks to the attackmate-api-server via CLI or the python library.

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

The local attackmate should log in to the remote API server, send the referenced playbook, and
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

Installing The API Server With systemd
======================================

The recommended deployment is to let ``attackmate-ansible`` install the API
server. Internally, the role installs ``attackmate-api-server`` into the same
virtual environment as AttackMate and runs it as a dedicated systemd service
user.

The manual setup below mirrors the role's systemd installation. It assumes
AttackMate is already installed in ``/usr/local/share/attackmate`` and that its
virtual environment exists at ``/usr/local/share/attackmate/.venv``.

Create a dedicated service user:

.. code-block:: console

    sudo useradd --system --shell /usr/sbin/nologin --no-create-home attackmate-api

Clone and install the API server into the AttackMate virtual environment:

.. code-block:: console

    sudo git clone https://github.com/ait-testbed/attackmate-api-server.git /usr/local/share/attackmate-api-server
    cd /usr/local/share/attackmate-api-server
    sudo uv pip install --python /usr/local/share/attackmate/.venv/bin/python .
    sudo ln -sf /usr/local/share/attackmate/.venv/bin/attackmate-api /usr/local/bin/attackmate-api

Create the API log directory:

.. code-block:: console

    sudo mkdir -p /var/log/attackmate-api
    sudo chown attackmate-api:attackmate-api /var/log/attackmate-api
    sudo chmod 0755 /var/log/attackmate-api

Create TLS directories and a self-signed certificate. Replace ``10.0.0.5`` with
the API server address clients will connect to:

.. code-block:: console

    sudo install -d -m 0710 -o root -g attackmate-api /etc/ssl/private
    sudo install -d -m 0755 -o root -g root /etc/ssl/certs
    sudo openssl req -x509 -newkey rsa:4096 -sha256 -days 825 -nodes \
      -keyout /etc/ssl/private/attackmate.key \
      -out /etc/ssl/certs/attackmate.pem \
      -subj "/CN=10.0.0.5" \
      -addext "subjectAltName=IP:10.0.0.5,DNS:localhost"
    sudo chown root:attackmate-api /etc/ssl/private/attackmate.key
    sudo chmod 0640 /etc/ssl/private/attackmate.key
    sudo chmod 0644 /etc/ssl/certs/attackmate.pem

Create ``/usr/local/share/attackmate-api-server/.env``:

.. code-block:: console

    sudo install -o attackmate-api -g attackmate-api -m 0600 /dev/null /usr/local/share/attackmate-api-server/.env
    sudoedit /usr/local/share/attackmate-api-server/.env

Example ``.env``:

.. code-block:: text

    SSL_KEY_PATH="/etc/ssl/private/attackmate.key"
    SSL_CERT_PATH="/etc/ssl/certs/attackmate.pem"
    ATTACKMATE_CONFIG_PATH="/etc/attackmate.yml"
    WRITE_PLAYBOOK_LOGS_TO_DISK="False"
    LOG_DIR="/var/log/attackmate-api"
    ATTACKMATE_API_SERVER_PORT="8445"
    USERS='{"admin": "$argon2id$v=19$m=65536,t=3,p=4$..."}'

``USERS`` contains username-to-Argon2-hash mappings. You can generate a hash
with:

.. code-block:: console

    python3 -c "from argon2 import PasswordHasher; print(PasswordHasher().hash('securepassword'))"

Install the systemd unit at ``/etc/systemd/system/attackmate-api.service``:

.. code-block:: ini

    [Unit]
    Description=AttackMate API Server
    After=network.target

    [Service]
    Type=simple
    User=attackmate-api
    Group=attackmate-api
    WorkingDirectory=/usr/local/share/attackmate-api-server
    EnvironmentFile=/usr/local/share/attackmate-api-server/.env
    ExecStart=/usr/local/bin/attackmate-api
    Restart=on-failure

    NoNewPrivileges=yes
    PrivateTmp=yes
    ProtectSystem=full
    ProtectHome=yes

    [Install]
    WantedBy=multi-user.target

Enable and start the service:

.. code-block:: console

    sudo systemctl daemon-reload
    sudo systemctl enable --now attackmate-api
    sudo systemctl status attackmate-api

Copy ``/etc/ssl/certs/attackmate.pem`` from the server to the client and use it
as the ``cafile`` in the client's ``remote_config``.


Server Logs
===========

The systemd service logs are available with:

.. code-block:: console

    journalctl -u attackmate-api -f

If file logging is enabled for API playbook runs, inspect the configured log
directory, for example:

.. code-block:: console

    tail -f /var/log/attackmate-api/*_output.log
