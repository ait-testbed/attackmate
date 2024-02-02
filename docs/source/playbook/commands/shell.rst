
=====
shell
=====

Execute local shell-commands.

.. code-block:: yaml

   ###
   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $NMAP: /usr/bin/nmap

   commands:
     - type: shell
       cmd: $NMAP $SERVER_ADDRESS

.. confval:: cmd

   The command-line that should be executed locally.

   :type: str

.. confval:: creates_session

   A session name that identifies the session that is created when
   executing this command. This session-name can be used by using the
   option "session".

   :type: str

.. confval:: session

   Reuse an existing interactive session. This setting works only if another
   shell-command was executed with the command-option "creates_session" and "interactive" true

   :type: str

.. confval:: interactive

   When the shell-command is executed, the command will block until the execution finishes.
   However, for some exploits it is necessary to run a command and send keystrokes to an
   interactive session. For example run with the first command "vim" and with the second command
   send keystrokes to the open vim-session. In interactive-mode the command will try reading the
   output until no output is written for a certain amount of seconds.

   .. warning::

      Please note that you **MUST** send a newline when you execute a ssh-command interactively.

   :type: bool
   :default: ``False``

   .. code-block:: yaml

      commands:
        # creates new ssh-connection and session
        - type: shell
          cmd: "nmap --interactive\n"
          interactive: True
          creates_session: "attacker"

        # break out of the nmap-interactive-mode
        - type: shell
          cmd: "!sh\n"
          interactive: True
          session: "attacker"

.. confval:: command_timeout

   The interactive-mode works with timeouts while reading the output. If there is no output for some seconds,
   the command will stop reading.

   :type: int
   :default: ``15``

.. confval:: read

   Wait for output. This option is useful for interactive commands that do not return any output.
   Normally attackmate will wait until the command_timeout was reached. With read is False, attackmate
   will not wait for any output and simply return an empty string.

   :type: bool
   :default: ``True``
