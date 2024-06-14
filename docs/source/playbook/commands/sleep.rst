=====
sleep
=====

Sleep a certain amount of seconds.

.. code-block:: yaml

   ###
   commands:
     - type: sleep
       seconds: 60


.. confval:: min_sec

   This option defines the minimum seconds to sleep. This
   is only relevant if option **random** is set to True

   :type: int
   :default: ``0``


.. confval:: seconds

   This options sets the seconds to sleep. If the option
   **random** is set to True, this option is the maximum time
   to sleep.

   :type: int
   :default: ``1``
   :required: True


.. confval:: random

  This option allows to randomize the seconds to wait. The minimum
  and maximum seconds for the range can be set by **min_sec** and
  **seconds**.


  :type: bool
  :default: ``False``


  The following example will take a random amount of seconds between 30 seconds
  and 60 seconds:

  .. code-block:: yaml

     ###
     commands:
       - type: sleep
         seconds: 60
         min_sec: 30
         random: True


.. confval:: cmd

  This option is ignored

  :type: str
  :default: ``sleep``
