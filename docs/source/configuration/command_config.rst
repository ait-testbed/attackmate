==========
cmd_config
==========

Stores global variables for command options. These are settings for **all** commands.

.. code-block:: yaml

   ###
   cmd_config:
     loop_sleep: 5

.. confval:: loop_sleep

   All commands can be configured to be executed in a loop. For example: if a command
   does not deliver the expected output, the command can be executed again until the
   output has the expected value. Between the executions can be a sleep time of certain
   seconds.

   :type: int
   :default: 5
