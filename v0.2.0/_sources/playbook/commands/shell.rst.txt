
=====
shell
=====

Execute local shell-commands.

.. code-block:: yaml

   ###
   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $NMAP: /usr/bin/nmap

   commands:
     - type: shell
       cmd: $NMAP $SERVER_ADDRESS

.. confval:: cmd

   The command-line that should be executed locally.

   :type: str
