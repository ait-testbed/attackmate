====
vars
====

Variables can be defined in the key/value-format. The variables
can be used in certain configuration places and are just placeholders
for the values. Currently they can only be used for string-type variables
of commands!

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

.. note::

   Please note that the dollar sign("$") is now reserved for variables.
   If you need the dollar sign, use "$$" instead! For more information
   see `string.Template <https://docs.python.org/3.8/library/string.html#string.Template>`_

Builtin Variables
=================

The following variables are set by the system:

``RESULT_STDOUT`` is set after every command execution and stores the result output.

``RESULT_CODE`` is set after every command execution and stores the returncode.

``LAST_MSF_SESSION`` is set every time after a new metasploit session was created and contains the session number.
