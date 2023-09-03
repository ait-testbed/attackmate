.. _commands:

========
Commands
========

The *'commands-section'* holds a list of AttackMate-commands that are executed sequentially from
top to bottom.

Every command, regardless of the type has the following general options:

.. confval:: save

   Save the output of the command to a file.

   :type: str

   .. code-block:: yaml

      commands:
        - type: shell
          cmd: nmap localhost
          save: /tmp/nmap_localhost.txt

.. confval:: exit_on_error

   If this option is true, attackmate will stop the run if the command returns with a return code
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


The next pages will describe all possible commands in detail.

.. toctree::
   :maxdepth: 4
   :hidden:

   shell
   sleep
   ssh
   sftp
   msf-module
   msf-session
   regex
   debug
   mktemp
   sliver
   sliver-session
   father
