.. _variables:

=========
Variables
=========

Variables may be assigned to by a statement of the form of key-values.
Once assigned, they can be used as placeholders in command-settings. It
is unnecessary to begin variable names with a $-sign when defined in the
vars-section. However, when variables are placed in the commands section,
they always must start with a $-sign.

.. code-block:: yaml

   ###
   vars:
     $SERVER_ADDRESS: 192.42.0.254
     # the $-sign is not necessary here:
     $NMAP: /usr/bin/nmap

   commands:
     - type: shell
       # the $-sign is required when using the variable:
       cmd: $NMAP $SERVER_ADDRESS

.. note::

   For more information about using the variables see `string.Template <https://docs.python.org/3/library/string.html#string.Template>`_

Builtin Variables
=================

The following variables are set by the system:

``RESULT_STDOUT`` is set after every command execution and stores the result output.

``RESULT_CODE`` is set after every command execution and stores the returncode.

``LAST_MSF_SESSION`` is set every time after a new metasploit session was created and contains the session number.

``LAST_FATHER_PATH`` is set every time when a father-rootkit was generated.
