=====
shell
=====

Execute local shell commands.

.. code-block:: yaml

   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $NMAP: /usr/bin/nmap

   commands:
     - type: shell
       cmd: $NMAP $SERVER_ADDRESS

.. confval:: cmd

   The command line to execute locally. Supports variable substitution.

   :type: str
   :required: True

.. confval:: command_shell

   The shell used to execute commands.

   :type: str
   :default: ``/bin/sh``
   :required: False

Interactive Mode
----------------

.. confval:: interactive

   Run the command in interactive mode.

   :type: bool
   :default: ``False``
   :required: False

   Instead of waiting for the command to finish,
   AttackMate reads output until no new output appears for :confval:`command_timeout`
   seconds. Useful for commands that require follow-up keystrokes (e.g. opening ``vim``
   and sending input in a subsequent command).

   This mode works only on Unix and Unix-like systems.

   .. warning::

      Commands executed in interactive mode **MUST** end with a newline character (``\n``).

   .. code-block:: yaml

      commands:
        # Open nmap in interactive mode and create a named session:
        - type: shell
          cmd: "nmap --interactive\n"
          interactive: True
          creates_session: attacker

        # Send a command to the open interactive session:
        - type: shell
          cmd: "!sh\n"
          interactive: True
          session: attacker

.. confval:: creates_session

   Name to assign to the interactive session opened by this command. Can be reused
   in subsequent commands via :confval:`session`.

   Only meaningful when :confval:`interactive` is ``True``.

   :type: str
   :required: False

.. confval:: session

   Name of an existing interactive session to reuse. The session must have been
   created previously via :confval:`creates_session` with :confval:`interactive`
   set to ``True``.

   :type: str
   :required: False

.. confval:: command_timeout

   Seconds to wait for new output before stopping in interactive mode.

   :type: int
   :default: ``15``
   :required: False

.. confval:: read

   Wait for output after executing the command. Set to ``False`` to return
   immediately with an empty result, useful for fire-and-forget interactive
   commands that produce no output.

   :type: bool
   :default: ``True``
   :required: False

Binary Mode
-----------

.. confval:: bin

   Enable binary mode. In this mode, ``cmd`` must be a hex-encoded string representing
   the raw bytes to execute.

   :type: bool
   :default: ``False``
   :required: False

   .. code-block:: yaml

      commands:
        # "6964" is the hex encoding of "id":
        - type: shell
          cmd: "6964"
          bin: true
