=====
debug
=====

The ``debug`` command prints messages and variables to the console. It is intended for
troubleshooting playbooks and does not modify ``RESULT_STDOUT`` (:ref:`builtin variables <builtin-variables>`).

   .. code-block:: yaml

      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $NMAP: /usr/bin/nmap

      commands:
        - type: debug
          cmd: "$NMAP $SERVER_ADDRESS"
          varstore: True

.. confval:: cmd

   A message to print to the console. Supports variable substitution.

   :type: str
   :default: ``empty_string``
   :required: False


.. confval:: varstore

   Print out all variables currently stored in the VariableStore.

   :type: bool
   :default: ``False``
   :required: False

.. confval:: exit

   This setting causes the programm to exit when the command was
   executed. It will exit with an error in order to indicate
   that this is an intentional early termination.

   :type: bool
   :default: ``False``
   :required: False

.. confval:: wait_for_key

   Pause execution until the user presses Enter. Useful for stepping through a
   playbook manually.

   :type: bool
   :default: ``False``
   :required: False
