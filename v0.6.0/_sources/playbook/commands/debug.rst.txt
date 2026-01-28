=====
debug
=====

This command prints out strings and variables and is for debugging
purposes/printing to the console only. This command does not modify the Builtin Variable ``RESULT_STDOUT``.

   .. code-block:: yaml

      ###
      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $NMAP: /usr/bin/nmap

      commands:
        - type: debug
          cmd: "$NMAP $SERVER_ADDRESS"
          varstore: True

.. confval:: cmd

   A message to print on the screen.

   :type: str
   :default: ``empty_string``


.. confval:: varstore

   Print out all variables that are stored in the VariableStore.

   :type: bool
   :default: ``False``

.. confval:: exit

   This setting causes the programm to exit when the command was
   executed. It will exit with an error in order to indicate
   that this is an exceptional break.

   :type: bool
   :default: ``False``

.. confval:: wait_for_key

   This setting causes the programm to pause until the user
   hits the enter key.

   :type: bool
   :default: ``False``
