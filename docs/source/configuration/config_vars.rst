====
vars
====

Variables can be defined in the key/value-format. The variables
can be used in certain configuration places and are just placeholders
for the values. Currently they can only be used for "cmd"

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
