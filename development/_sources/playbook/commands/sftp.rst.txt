====
sftp
====

Upload or download files using SSH. This command is
also executed by the SSHExecutor and therefor all
ssh-related settings can be used. SSH-sessions can also
be used with the sftp-command!

.. note::

   This command caches all the settings so
   that they only need to be defined once.

.. code-block:: yaml

   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $SSH_SERVER: 10.10.10.19

   commands:
     - type: sftp
       cmd: put
       local_path: /tmp/linpeas.sh
       remote_path: /tmp/linpeas.sh
       hostname: $SSH_SERVER
       username: aecid
       key_filename: "/home/alice/.ssh/id_rsa"
       creates_session: "attacker"

     # cached ssh-settings. creates new ssh-connection
     - type: sftp
       cmd: get
       remote_path: /etc/passwd
       local_path: /tmp/remote_passwd

     # reuses existing session "attacker"
     - type: ssh
       session: "attacker"
       cmd: "id"

.. confval:: cmd

   SFTP-command to use. Valid commands are *put* or *get*.

   :type: str
   :required: ``True``

.. confval:: remote_path

   The filepath on the remote machine.

   :type: str
   :required: ``True``

.. confval:: local_path

   The filepath on the local machine.

   :type: str
   :required: ``True``

.. confval:: mode

   The file permissions on the remote file(e.g. *755*).

   :type: str


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
