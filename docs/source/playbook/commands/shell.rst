
=====
shell
=====

Execute local shell-commands.

.. confval:: cmd

   The command-line that should be executed locally.

   :type: str


   .. code-block:: yaml
      ###
      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $NMAP: /usr/bin/nmap

      commands:
        - type: shell
          cmd: $NMAP $SERVER_ADDRESS
