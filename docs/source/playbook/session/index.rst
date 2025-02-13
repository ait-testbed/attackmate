.. _session:

=====================
Sessions, Interactive
=====================

Many commands of AttackMate support the setting "session" or "interactive.
This chapter is about these important concepts of AttackMate.

Session
-------

AttackMate executes all commands stateless. Therefore, each command is executed in a new "environment".
What "environment" means depends on the type of the command. For example, every stateless shell
command spawns a new shell process. As illustrated in the following image, every shell command
is executed in a new `/bin/sh` process.

.. image:: /images/Stateless-Command.png

The ssh-command on the other hand, establishes with every new stateless execution a new SSH connection.
AttackMate will log in to the target with every single command execution. However, sometimes you want the AttackMate not to log on to the target system every time you execute a command. To achieve this, you can use sessions.

Many commands support the "creates_session" option. This allows you to specify a session name and AttackMate saves the environment of the command. By using the session name for further commands, it is possible to continue where the previous command left off at any time. The following figure shows how the first command uses create_session to execute a stateful command. The third command can then continue in the same environment as the first command by using the session.

.. image:: /images/Stateful-Command.png

Interactive
-----------

Many commands work in such a way that they first execute something and then collect and return the output. Sometimes, however, commands are executed that do not produce any output. In such cases, AttackMate would wait forever. One such example would be executing the text editor vim on the command line. Vim is started and waits for input. AttackMate gets no output, or the process does not terminate and so it waits forever. Interactive mode is available for such cases. This mode causes commands to be executed for a limited time only. After this time has elapsed, AttackMate continues.  The following example shows how AttackMate executes vim with the help of a session and the interactive mode in a shell command and then types keyboard strokes into the open vim sessions.

.. code-block:: yaml

   commands:
     - type: shell
       cmd: "vim /tmp/test\n"
       interactive: True
       creates_session: vim

     - type: shell
       cmd: ":inoremap jj <ESC>\n"
       interactive: True
       session: vim

     - type: shell
       cmd: "o"
       interactive: True
       session: vim

     - type: shell
       cmd: "Hello World"
       interactive: True
       session: vim

     - type: shell
       cmd: "jj"
       interactive: True
       session: vim

     - type: shell
       cmd: ":wq!\n"
       interactive: True
       session: vim

.. warning::

      Please note that you **MUST** send a newline when you execute interactive commands!
