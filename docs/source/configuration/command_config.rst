==========
cmd_config
==========

Stores global variables for command options.
These are settings for **all** commands.

.. code-block:: yaml

   cmd_config:
     loop_sleep: 5
     command_delay: 0

.. confval:: loop_sleep

   All commands can be configured to be executed in a loop. For example:
   retrying until the output of a command matches an expected value,
   with an optional sleep interval between attempts.

   :type: int
   :default: 5

.. confval:: command_delay

   A delay in seconds applied **before** each command in the playbook.
   Does not apply to ``debug``, ``setvar``, and ``sleep`` commands.

   :type: float
   :default: 0
