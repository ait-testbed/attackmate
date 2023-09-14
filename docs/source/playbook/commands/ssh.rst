===
ssh
===

Execute commands on a remote server via SSH.

.. note::

   This command caches all the settings so
   that they only need to be defined once.

.. code-block:: yaml

   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $SSH_SERVER: 10.10.10.19

   commands:
     # creates new ssh-connection and session
     - type: ssh
       cmd: nmap $SERVER_ADDRESS
       hostname: 10.10.10.19
       username: aecid
       key_filename: "/home/alice/.ssh/id_rsa"
       creates_session: "attacker"

     # cached ssh-settings. creates new ssh-connection
     - type: ssh
       cmd: "echo $SERVER_ADDRESS"

     # reuses existing session "attacker"
     - type: ssh
       session: "attacker"
       cmd: "id"

.. confval:: hostname

   This option sets the hostname or ip-address of the
   remote ssh-server.

   :type: str

.. confval:: port

   Port to connect to on the remote host.

   :type: int
   :default: ``22``

.. confval:: username

   Specifies the user to log in as on the remote machine.

   :type: str

.. confval:: password

   Specifies the password to use. An alternative would be to use a key_file.

   :type: str

.. confval:: passphrase

   Use this passphrase to decrypt the key_file. This is only necessary if the
   keyfile is protected by a passphrase.

   :type: str

.. confval:: key_filename

   Path to the keyfile.

   :type: str


.. confval:: timeout

   The timeout to drop a connection attempt in seconds.

   :type: float

.. confval:: clear_cache

   Normally all settings for ssh-connections are cached. This allows to defined
   all settings in one command and all following commands can reuse these settings
   without set them in every single command. If a new connection with different
   settings should be configured, this setting allows to reset the cache to default
   values.

   :type: bool
   :default: ``False``

   .. note::

       This setting will not clear the session store.

.. confval:: creates_session

   A session name that identifies the session that is created when
   executing this command. This session-name can be used by using the
   option "session"

   :type: str

.. confval:: session

   Reuse an existing ssh-session. This setting works only if another
   ssh-command was executed with the command-option "creates_session"

   :type: str

.. confval:: jmp_hostname

   This option sets the hostname or ip-address of the
   remote jump server.

   :type: str

.. confval:: jmp_port

   Port to connect to on the jump-host.

   :type: int
   :default: ``22``

.. confval:: jmp_username

   Specifies the user to log in as on the jmp-host.

   :type: str
   :default: ``same as username``

.. confval:: interactive

   When the ssh-command is executed, the command will block until the ssh-execution finishes.
   However, for some exploits it is necessary to run a command and send keystrokes to an
   interactive session. For example run with the first command "vim" and with the second command
   send keystrokes to the open vim-session. In interactive-mode the command will try reading the
   output until no output is written for a certain amount of seconds. If the output ends with any
   string found in ``prompts``, it will stop immediately.

   .. warning::

      Please note that you **MUST** send a newline when you execute a ssh-command interactively.

   :type: bool
   :default: ``False``

   .. code-block:: yaml

      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $SSH_SERVER: 10.10.10.19

      commands:
        # creates new ssh-connection and session
        - type: ssh
          cmd: "nmap --interactive\n"
          interactive: True
          hostname: 10.10.10.19
          username: aecid
          key_filename: "/home/alice/.ssh/id_rsa"
          creates_session: "attacker"

        # break out of the nmap-interactive-mode
        - type: ssh
          cmd: "!sh\n"
          interactive: True
          session: "attacker"

.. confval:: command_timeout

   The interactive-mode works with timeouts while reading the output. If there is no output for some seconds,
   the command will stop reading.

   :type: int
   :default: ``15``

.. confval:: prompts

   In interactive-mode the command will try reading the output for a certain amount of seconds. If the output
   ends with any string found in ``prompts``, the command will stop immediately.

   :type: list[str]
   :default: ``["$ ", "# ", "> "]``

   .. code-block:: yaml

      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $SSH_SERVER: 10.10.10.19

      commands:
        # creates new ssh-connection and session
        - type: ssh
          cmd: "nmap --interactive\n"
          interactive: True
          prompts:
            - "$ "
            - "# "
            - "> "
            - "% "
          hostname: 10.10.10.19
          username: aecid
          key_filename: "/home/alice/.ssh/id_rsa"
          creates_session: "attacker"
