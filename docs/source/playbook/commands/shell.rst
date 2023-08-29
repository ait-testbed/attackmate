
=====
shell
=====

This command executes local shell-commands.

.. confval:: cmd

   cmd stores the command-line that should be executed locally.

   :type: str


   .. code-block:: yaml

      ###
      msf_config:
        password: top-secret
        server: 10.18.3.86

      vars:
        $SERVER_ADDRESS: 192.42.0.254
        $NMAP: /usr/bin/nmap

      commands:
        - type: shell
          cmd: $NMAP $SERVER_ADDRESS
