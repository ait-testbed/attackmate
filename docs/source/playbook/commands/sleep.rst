=====
sleep
=====

Pause execution for a fixed or randomised number of seconds.

.. code-block:: yaml

   commands:
   # Sleep for 60 seconds
     - type: sleep
       seconds: 60


.. confval:: seconds

   Number of seconds to sleep. When :confval:`random` is ``True``, this serves as
   the upper bound of the random range.

   :type: int
   :default: ``1``
   :required: True


.. confval:: random

  Sleep for a random duration between :confval:`min_sec` and :confval:`seconds`
  instead of a fixed duration.

  :type: bool
  :default: ``False``
  :required: False


.. confval:: min_sec

   Lower bound in seconds for the random sleep range. Only used when
   :confval:`random` is ``True``.

   :type: int
   :default: ``0``
   :required: False

  .. code-block:: yaml

     commands:
     # Sleep for a random duration between 30 and 60 seconds
       - type: sleep
         seconds: 60
         min_sec: 30
         random: True


.. confval:: cmd

  This option is ignored. It is only present to allow the use of the generic command syntax and does not have any effect on the behavior of the command.

  :type: str
  :default: ``sleep``
