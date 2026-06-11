==========
cmd_config
==========

Stores global variables for command options.
These are settings for **all** commands.

.. code-block:: yaml

   cmd_config:
     loop_sleep: 5
     command_delay: 0
     command_delay_jitter: false
     command_delay_jitter_min: 0.5
     command_delay_jitter_max: 2.0

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

.. confval:: command_delay_jitter

   When ``true``, randomizes the per-command delay. The effective delay is calculated as
   ``command_delay ± random(command_delay_jitter_min, command_delay_jitter_max)``,
   clamped to a minimum of ``0``. Has no effect when ``command_delay_jitter``
   is ``false``.

   :type: bool
   :default: false

.. confval:: command_delay_jitter_min

   Lower bound of the jitter offset in seconds. Only used when
   :confval:`command_delay_jitter` is ``true``.

   :type: float
   :default: 0.5

.. confval:: command_delay_jitter_max

   Upper bound of the jitter offset in seconds. Only used when
   :confval:`command_delay_jitter` is ``true``.

   :type: float
   :default: 2.0
