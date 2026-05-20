.. _sftp:

====
sftp
====

Upload or download files over SSH. This command shares the same connection settings and
session cache as the :ref:`ssh <ssh>` command — all SSH options apply, and sessions
created by either command can be reused by the other.

.. note::

   This command caches all settings so that they only need to be defined once.

   Background mode with a session is not supported for this commands.


.. code-block:: yaml

   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $SSH_SERVER: 10.10.10.19

   commands:
     # Upload a file and create a named session:
     - type: sftp
       cmd: put
       local_path: /tmp/linpeas.sh
       remote_path: /tmp/linpeas.sh
       hostname: $SSH_SERVER
       username: aecid
       key_filename: "/home/alice/.ssh/id_rsa"
       creates_session: attacker

     # Download a file using cached connection settings, creates new connection:
     - type: sftp
       cmd: get
       remote_path: /etc/passwd
       local_path: /tmp/remote_passwd

     # Reuse the "attacker" session from the first command in an ssh command:
     - type: ssh
       session: attacker
       cmd: id

File Transfer
-------------

.. confval:: cmd

   The SFTP operation to perform.

   * ``put`` - upload a file from the local machine to the remote host
   * ``get`` - download a file from the remote host to the local machine

   :type: str
   :required: True

.. confval:: local_path

   Path to the file on the local machine.

   :type: str
   :required: True

.. confval:: remote_path

   Path to the file on the remote machine.

   :type: str
   :required: True

.. confval:: mode

   File permissions to set on the remote file after upload (e.g. ``755``).

   :type: str
   :required: False

Connection
----------

.. confval:: hostname

   Hostname or IP address of the remote SSH server.

   :type: str

.. confval:: port

   Port to connect to on the remote host.

   :type: int
   :default: ``22``

.. confval:: username

   Username to authenticate as on the remote host.

   :type: str

.. confval:: password

   Password for authentication. An alternative is to use :confval:`key_filename`.

   :type: str

.. confval:: key_filename

   Path to a private key file for authentication.

   :type: str

.. confval:: passphrase

   Passphrase to decrypt :confval:`key_filename`, if the key is passphrase-protected.

   :type: str

.. confval:: timeout

   Timeout in seconds for connection attempts.

   :type: float

.. confval:: clear_cache

   Clear all cached connection settings before this command runs, allowing a fresh
   connection to be configured. (Normally all settings for ssh-connections are cached. This allows to define
   all settings in one command and reuse them in the following commands without having to redefine them)


   :type: bool
   :default: ``False``
   :required: False

Sessions
--------

.. confval:: creates_session

   Name to assign to the session opened by this command. Can be reused in subsequent
   ``sftp`` or ``ssh`` commands via :confval:`session`.

   :type: str

.. confval:: session

   Name of an existing session to reuse. The session must have been created previously
   via :confval:`creates_session` in an ``sftp`` or ``ssh`` command.

   :type: str
   :required: False

Jump Host
---------

.. confval:: jmp_hostname

   Hostname or IP address of an SSH jump host to tunnel through.

   :type: str

.. confval:: jmp_port

   Port to connect to on the jump host.

   :type: int
   :default: ``22``

.. confval:: jmp_username

   Username to authenticate as on the jump host.

   :type: str
   :default: same as :confval:`username`
