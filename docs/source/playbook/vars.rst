.. _variables:

=========
Variables
=========

Variables are defined as key-value pairs in the ``vars`` section and can be used as
placeholders in command settings. Variable names do not require a ``$`` prefix when
defined in the ``vars`` section, but **MUST** be prefixed with ``$`` when referenced
in the ``commands`` section.
If an environment variable with the prefix ``ATTACKMATE_`` exists with the same name,
it will override the playbook variable. For example,  the playbook variabel ``$FOO`` will
be overwritten by the environment variabel ``$ATTACKMATE_FOO``.

.. code-block:: yaml

   vars:
     # the $-sign is optional here:
     $SERVER_ADDRESS: 192.42.0.254
     $NMAP: /usr/bin/nmap

   commands:
     - type: shell
       # the $-sign is required when referencing a variable:
       cmd: $NMAP $SERVER_ADDRESS

.. note::

   Variable substitution uses Python's `string.Template
   <https://docs.python.org/3/library/string.html#string.Template>`_ syntax.


.. note::

   Variables in ``cmd`` settings of a ``loop`` command will be substituted on every iteration of the loop, see the  :ref:`loop` command for details.


.. _builtin-variables:

Builtin Variables
=================

The following variables are set automatically by AttackMate during execution:

``RESULT_STDOUT`` Stores the standard output of the most recently executed command. Not set by ``debug``, ``regex``, or ``setvar`` commands.

``RESULT_CODE`` Stores the return code of the most recently executed command.

``LAST_MSF_SESSION`` Set whenever a new Metasploit session is created. Contains the session number.

``LAST_SLIVER_IMPLANT`` Set whenever a new Sliver implant is generated. Contains the path to the implant file.

``LAST_FATHER_PATH`` Set whenever a Father rootkit is generated. Contains the path to the rootkit.

``REGEX_MATCHES_LIST`` Set every time a regex command yields matches. Contains a list of all matches. If ``sub`` or ``split`` finds no match, the original input string is returned.
