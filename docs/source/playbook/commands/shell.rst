.. _shell:

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
   seconds. Useful for programs that keep running and accept follow-up commands,
   such as ``nmap --interactive``.

   This mode works only on Unix and Unix-like systems.

   .. note::

      The command still runs on a pipe, not a terminal. Editors such as ``vim``
      and ``nano``, and anything that prompts for a password like ``sudo``, need
      :confval:`pty` instead.

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

   Seconds to wait for new output before stopping in interactive or
   pseudo-terminal mode.

   In pseudo-terminal mode, ``0`` means "no time limit": the command then reads
   until one of the :confval:`prompts` matches, so at least one prompt must be
   configured.

   :type: int
   :default: ``10``
   :required: False

.. confval:: read

   Wait for output after executing the command. Set to ``False`` to return
   immediately with an empty result, useful for fire-and-forget interactive
   commands that produce no output.

   :type: bool
   :default: ``True``
   :required: False

Pseudo-Terminal Mode
--------------------

Interactive mode runs a command for a limited time, but the command still talks
to a pipe. Many programs behave differently, or refuse to run at all, when they
are not attached to a terminal:

* ``vim`` and ``nano`` report *"Output is not to a terminal"* and never draw a screen.
* ``sudo``, ``su`` and ``ssh`` read passwords from ``/dev/tty`` rather than from
  standard input, so a password sent as a normal command never reaches them.

Pseudo-terminal mode gives the shell a real terminal, which makes all of these work.

.. confval:: pty

   Run the command behind a pseudo-terminal.

   :type: bool
   :default: ``False``
   :required: False

   This mode works only on Unix and Unix-like systems; on Windows the command
   fails with a non-zero return code instead of running.

   Output is read exactly as in :confval:`interactive` mode - until no new output
   has arrived for :confval:`command_timeout` seconds, or one of the
   :confval:`prompts` matches - so ``interactive`` does not need to be set as well.

   .. code-block:: yaml

      commands:
        # Open vim in a pseudo-terminal and keep the session:
        - type: shell
          cmd: "vim /tmp/notes\n"
          pty: True
          creates_session: editor

        # Type a line and save. <ESC> is sent as a real escape key:
        - type: shell
          cmd: "iHello World<ESC>:wq!\n"
          pty: True
          session: editor

.. confval:: raw

   Put the terminal in raw mode, disabling ``icanon``, ``echo``, ``isig`` and
   ``icrnl``.

   :type: bool
   :default: ``True``
   :required: False

   A pseudo-terminal otherwise comes up in the line-editing mode meant for a
   human at a keyboard. That is invisible for a local full-screen program, which
   sets raw mode itself on startup, and fatal when the session is a *transport* -
   a program running on a remote host can never change the line discipline of a
   terminal on this one:

   * ``icanon`` holds a lone control key, such as nano's ``<C-o>``, in the local
     line buffer, so it never reaches the far end;
   * ``isig`` turns ``<C-c>`` into a signal against the local shell instead of
     sending it onward;
   * ``echo`` returns every command, so a session's output contains the commands
     as well as their results - and that is what :confval:`error_if` and
     :confval:`save` then see.

   Set it to ``False`` when you want the local signal behaviour, for example to
   interrupt a local program with ``<C-c>``.

   .. note::

      With ``icrnl`` off, a full-screen program expects a real carriage return.
      Send ``<CR>`` rather than ``\n`` to answer a prompt inside one - nano's
      "File Name to Write" prompt, for instance. Shell command lines are
      unaffected and still end with ``\n``.

.. confval:: expand_keys

   Translate key names such as ``<ESC>``, ``<CR>``, ``<TAB>``, ``<UP>``, ``<F1>``
   and ``<C-x>`` (Ctrl-X) in :confval:`cmd` into the bytes a terminal sends.

   :type: bool
   :default: ``True`` when :confval:`pty` is set, otherwise ``False``
   :required: False

   Set it to ``False`` to send such text literally, or write ``<LT>`` to produce
   a single ``<`` while expansion is on. Unrecognised markers are left alone, so
   ordinary text containing angle brackets is unaffected. Key names are ignored
   in :confval:`bin` mode, which always sends raw bytes.

   .. warning::

      Some key names are also ordinary HTML tags. ``<del>PAYLOAD</del>`` and
      ``<ins>PAYLOAD</ins>`` contain the key names ``<DEL>`` and ``<INS>``, so
      with expansion on they are rewritten into keypresses. Set
      ``expand_keys: False`` on any command carrying markup - a reproduced XSS
      or HTML-injection payload, for instance.

.. confval:: screen

   Render the output as a terminal screen instead of a stream of bytes.

   :type: bool
   :default: ``False``
   :required: False

   Full-screen programs draw by moving the cursor around, so their raw output is
   a series of fragments in write order rather than what a user would see. In
   screen mode AttackMate emulates a terminal and returns the resulting text,
   which is what makes :confval:`error_if` and :confval:`save` useful against
   programs like ``nano`` or ``top``.

   Two consequences are worth knowing:

   * The result is the whole visible screen, so lines from an earlier command in
     the same session appear again as long as they are still on screen.
   * Whether a session renders a screen is decided by the command that creates
     it. A later command on the same session cannot switch it on.

   .. code-block:: yaml

      commands:
        - type: shell
          cmd: "nano /tmp/notes\n"
          pty: True
          screen: True
          creates_session: editor

        # Ctrl-O writes the file, Ctrl-X leaves nano:
        - type: shell
          cmd: "Hello<C-o><CR><C-x>"
          pty: True
          session: editor

.. confval:: prompts

   Strings that end a read early. As soon as the output ends with one of them,
   AttackMate stops waiting instead of sitting out :confval:`command_timeout`.

   :type: list[str]
   :default: ``[]``
   :required: False

.. confval:: read_timeout

   Total number of seconds one read may take, however much output arrives.

   :type: int
   :default: ``None`` (no bound)
   :required: False

   :confval:`command_timeout` measures *silence*, so it cannot end a command
   that keeps producing output. This bounds the whole read instead.

.. confval:: wait_for_exit

   Return when the command has actually finished, and report its real exit
   status.

   :type: bool
   :default: ``False``
   :required: False

   Inside a session there is nothing to wait on - the shell does not exit
   between commands - so "run this and tell me when it is done" is unanswerable
   unless the command reports it. AttackMate therefore appends
   ``; echo "$?<marker>"`` and reads until the marker appears, which supplies
   both the completion signal and the exit status. The marker is removed from
   the output.

   Use it for a long step that produces no prompt and may fall silent while
   still running, such as an enumeration script.

   .. note::

      This works for both :confval:`pty` and :confval:`interactive` sessions. A
      plain non-interactive command needs no marker and does not get one: it is
      run to completion anyway, and already reports a real ``exit-status``.

   .. warning::

      This is the only option that rewrites the command before it runs. If a
      playbook has to reproduce commands verbatim, leave it off. It cannot be
      combined with :confval:`bin`, which sends raw bytes.

   .. code-block:: yaml

      commands:
        - type: shell
          cmd: ./linpeas.sh
          pty: True
          wait_for_exit: True
          read_timeout: 900

.. confval:: term

   Value of the ``TERM`` environment variable given to the command.

   :type: str
   :default: ``xterm-256color``
   :required: False

.. confval:: pty_rows

   Height of the terminal reported to the command.

   :type: int
   :default: ``24``
   :required: False

.. confval:: pty_cols

   Width of the terminal reported to the command.

   :type: int
   :default: ``80``
   :required: False

   Terminal size decides where a full-screen program wraps and truncates its
   output, and in :confval:`screen` mode it also decides how much text the
   result can contain.

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
