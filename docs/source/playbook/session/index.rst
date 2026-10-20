.. _session:

=====================
Sessions, Interactive
=====================

Many AttackMate commands support the ``creates_session``, ``session``, and ``interactive``
options. This page explains these concepts and when to use them.

Session
--------

By default, AttackMate executes all commands statelessly — each command runs in a fresh
environment. What "environment" means depends on the command type: a ``shell`` command
spawns a new ``/bin/sh`` process, an ``ssh`` command opens a new SSH connection, and so on.

.. image:: /images/Stateless-Command.png

This means that directory changes, environment variables, or open connections from one
command are not visible to the next. To persist state across commands, AttackMate supports
sessions.

Any command that supports the ``creates_session`` option will save its environment under
the given session name. Subsequent commands can then reference that name via ``session``
to continue working in the same environment, as illustrated below.

.. image:: /images/Stateful-Command.png

Interactive
-----------

Most commands work by executing something and waiting for the process to finish before
collecting its output. This breaks down for interactive programs that wait for user input
and never terminate on their own — for example, a command that opens a pager would cause
AttackMate to wait forever for output that never comes.

Interactive mode solves this by running a command for a limited time only. Instead of
waiting for the process to finish, AttackMate reads output until no new output has arrived
for a configurable timeout period, then moves on to the next command.

.. warning::

   Commands executed in interactive mode **MUST** end with a newline character (``\n``).

The following example starts ``nmap`` in its interactive mode and then sends it a
second command through the same session:

.. code-block:: yaml

   commands:
     # Start nmap in interactive mode and create a session:
     - type: shell
       cmd: "nmap --interactive\n"
       interactive: True
       creates_session: scanner

     # Send a command to the running program:
     - type: shell
       cmd: "!sh\n"
       interactive: True
       session: scanner

Pseudo-Terminal
---------------

Interactive mode limits how long AttackMate waits, but the command still talks to a
pipe rather than a terminal. Programs that insist on a terminal are not satisfied by
that: ``vim`` and ``nano`` report *"Output is not to a terminal"* and never draw a
screen, and ``sudo``, ``su`` and ``ssh`` read passwords from ``/dev/tty`` instead of
standard input, so a password sent as an ordinary command never reaches them.

Setting ``pty: True`` on a ``shell`` command gives it a real terminal and makes all of
these work. Key names such as ``<ESC>`` are then sent as actual keystrokes.

.. note::

   ``ssh`` commands already get a terminal from the remote host when
   ``interactive`` is set, so they have no ``pty`` option.

The following example opens ``vim``, types text, and saves the file:

.. code-block:: yaml

   commands:
     # Open vim in a pseudo-terminal and create a session:
     - type: shell
       cmd: "vim /tmp/test\n"
       pty: True
       creates_session: vim

     # Enter insert mode and type some text:
     - type: shell
       cmd: "oHello World"
       pty: True
       session: vim

     # Leave insert mode with a real Escape key, then save and quit:
     - type: shell
       cmd: "<ESC>:wq!\n"
       pty: True
       session: vim

For programs that repaint the screen, such as ``nano`` or ``top``, add ``screen: True``
so that AttackMate returns the text as displayed rather than the raw drawing
instructions. See :ref:`commands` for the full list of options.

Driving a program on another host
---------------------------------

A pseudo-terminal is also what makes a session usable as a *transport* — driving a
program that runs on the target rather than locally. Two things are worth knowing
before doing that.

**The terminal is on the attacker's host.** A program running on the target cannot
change its line discipline, which is why ``pty`` sessions are raw by default. In the
default line-editing mode a lone ``<C-o>`` or ``<C-x>`` never leaves the local buffer,
and a ``<C-c>`` raises a signal against the local shell instead of travelling.

**The remote shell has no ``TERM``.** A shell reached through a reverse shell inherits
nothing from your environment, and ``pty.spawn`` on the target allocates a pts without
setting ``TERM``, so ncurses aborts before drawing anything:

.. code-block:: text

   Error opening terminal: unknown.

AttackMate cannot set this for you — it is an environment variable on a host it does
not control — so export it through the session itself, as
``examples/includes/upgrade_shell.yml`` does:

.. code-block:: yaml

   commands:
     # Upgrade the remote shell to a pty on the target:
     - type: shell
       cmd: "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'\n"
       pty: True
       session: foothold

     # ncurses needs this, or it refuses to draw:
     - type: shell
       cmd: "export TERM=xterm\n"
       pty: True
       session: foothold

     - type: shell
       cmd: "stty rows 24 columns 80\n"
       pty: True
       session: foothold
