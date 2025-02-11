.. _variables:

=========
Variables
=========

Variables may be assigned to by a statement of the form of key-values.
Once assigned, they can be used as placeholders in command-settings. It
is unnecessary to begin variable names with a $-sign when defined in the
vars-section. However, when variables are placed in the commands section,
they always must start with a $-sign.
If the same variable name with the prefix "ATTACKMATE_" exists as an
environment variable it will overwrite the playbook variable value.
i.e. the playbookvariabel $FOO will be overwritten be environment variabel
$ATTACKMATE_FOO.

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


.. note::

   variables in cmd settings of a loop command will be substituted on every iteration of the loop, see :ref:`loop`

Builtin Variables
=================

The following variables are set by the system:

``RESULT_STDOUT`` is set after every command execution (except for debug, regex and setvar commands) and stores the result output.

``RESULT_CODE`` is set after every command execution and stores the returncode.

``LAST_MSF_SESSION`` is set every time after a new metasploit session was created and contains the session number.

``LAST_SLIVER_IMPLANT`` is set every time after a new sliver implant was created and contains the path to the implant file.

``LAST_FATHER_PATH`` is set every time when a father-rootkit was generated.

``REGEX_MATCHES_LIST`` is set every time a regex command yields matches and it contains a list of all matches. Note that if sub or split does not have a match the input string is returned.
