.. _ssh:

===
ssh
===

Execute commands on a remote host via SSH.

.. note::

   This command caches all settings so
   that they only need to be defined once.

   Background mode with a session is not supported for this commands.

.. code-block:: yaml

   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $SSH_SERVER: 10.10.10.19

   commands:
     # Establish a new connection and create a named session:
     - type: ssh
       cmd: nmap $SERVER_ADDRESS
       hostname: $SSH_SERVER
       username: aecid
       key_filename: "/home/alice/.ssh/id_rsa"
       creates_session: attacker

     # Reuses cached settings, opens a new connection:
     - type: ssh
       cmd: echo $SERVER_ADDRESS

     # Reuses the existing "attacker" session:
     - type: ssh
       session: attacker
       cmd: id

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
   :default: ``60``
   :required: False

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
   commands via :confval:`session`.

   :type: str

.. confval:: session

   Name of an existing session to reuse. The session must have been created previously
   via :confval:`creates_session`.

   :type: str

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

Interactive Mode
----------------

.. confval:: interactive

   Run the command in interactive mode.

   :type: bool
   :default: ``False``
   :required: False

   Instead of waiting for the command to finish,
   AttackMate reads output until no new output appears for :confval:`command_timeout`
   seconds, or until the output ends with one of the strings in :confval:`prompts`.

   Useful for commands that require keystroke input (e.g. opening ``vim`` and then
   sending keystrokes in a follow-up command).

   .. warning::

      Commands executed in interactive mode **MUST** end with a newline character (``\n``).



   .. code-block:: yaml

      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $SSH_SERVER: 10.10.10.19

      commands:
        # Open nmap in interactive mode and create a session:
        - type: ssh
          cmd: "nmap --interactive\n"
          interactive: True
          hostname: $SSH_SERVER
          username: aecid
          key_filename: "/home/alice/.ssh/id_rsa"
          creates_session: attacker

        # Send a command to the open interactive session:
        - type: ssh
          cmd: "!sh\n"
          interactive: True
          session: attacker

.. confval:: command_timeout

   Seconds to wait for new output before stopping in interactive mode.

   :type: int
   :default: ``15``
   :required: False

.. confval:: prompts

   List of strings that signal the end of output in interactive mode. When the output
   ends with any of these strings, AttackMate stops reading immediately without waiting
   for the timeout. Set to an empty list to disable prompt detection.

   :type: list[str]
   :default: ``["$ ", "# ", "> "]``
   :required: False

   .. code-block:: yaml

      commands:
        # Custom prompt list:
        - type: ssh
          cmd: "nmap --interactive\n"
          interactive: True
          prompts:
            - "$ "
            - "# "
            - "> "
            - "% "
          hostname: $SSH_SERVER
          username: aecid
          key_filename: "/home/alice/.ssh/id_rsa"
          creates_session: attacker

   .. code-block:: yaml

      vars:
        $SSH_SERVER: 10.10.10.19
        # Disable prompt detection entirely:
        - type: ssh
          cmd: "id\n"
          interactive: True
          prompts: []
          hostname: $SSH_SERVER
          username: aecid
          password: password
          creates_session: attacker

Binary Mode
-----------

.. confval:: bin

   Enable binary mode. In this mode, ``cmd`` must be a hex-encoded string representing
   the raw bytes to send.

   :type: bool
   :default: ``False``
   :required: False

   .. code-block:: yaml

      commands:
        # "6964" is the hex encoding of "id":
        - type: ssh
          cmd: "6964"
          bin: True
          hostname: $SSH_SERVER
          username: aecid
          key_filename: "/home/alice/.ssh/id_rsa"
