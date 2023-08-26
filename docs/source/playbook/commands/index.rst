========
commands
========

The setting **commands** holds a list of commands that are executed sequentially from
top to bottom.

Every command, regardless of the type has the following options:

.. confval:: save

   Save the output of the command to a file.

   :type: str

   .. code-block:: yaml

      commands:
        - type: shell
          cmd: nmap localhost
          save: /tmp/nmap_localhost.txt

.. confval:: exit_on_error

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

.. toctree::
   :maxdepth: 4
   :hidden:

   shell
   sleep
   ssh
   msf-module
   msf-session
   regex
   debug
   sliver
   sliver-session
