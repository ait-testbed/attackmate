.. _variables:

=========
Variables
=========

Variables may be assigned to by a statement of the form of key-values.
Once assigned, they can be used as placeholders in command-settings. It
is unnecessary to begin variable names with a $-sign when defined in the
vars-section. However, when variables are placed in the commands section,
they always must start with a $-sign.


Environmental Variables
=======================

Variables names used in the format $SOME_VARIABLE in the commands-section that have NOT been defined in the vars-section will be replaced with
environmental variables loaded with os.environ(). Parsing the playbook will fail if the environmental variable can not be loaded.
Variable names already defined in the var-section take precedence, they will only be replaced with environmental variables if prefixed with "ATTACKMATE_".
For example ATTACKMATE_FOO defined in the vars section will be overwritten by env variable value if env variable FOO exists.



.. code-block:: yaml

   ###
   vars:
     $SERVER_ADDRESS: 192.42.0.254
     # the $-sign is not necessary here:
     NMAP: /usr/bin/nmap
     $ATTACKMATE_FOO: foo

   commands:
     - type: shell
       # the $-sign is required when using the variable:
       cmd: $NMAP $SERVER_ADDRESS
    - type: shell
       # This variable is not defined in the vars section and will be replaced by environmental variable:
       cmd: echo $SOME_ENV_VAR
    - type: shell
       # This variable will be replaced by the environmental variable FOO if it exists:
       cmd: echo $ATTACKMATE_FOO

.. note::

   For more information about using the variables see `string.Template <https://docs.python.org/3/library/string.html#string.Template>`_

Builtin Variables
=================

The following variables are set by the system:

``RESULT_STDOUT`` is set after every command execution and stores the result output.

``RESULT_CODE`` is set after every command execution and stores the returncode.

``LAST_MSF_SESSION`` is set every time after a new metasploit session was created and contains the session number.

``LAST_SLIVER_IMPLANT`` is set every time after a new sliver implant was created and contains the path to the implant file.

``LAST_FATHER_PATH`` is set every time when a father-rootkit was generated.
