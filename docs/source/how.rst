============
How it works
============

AttackMate executes playbooks consisting of commands, each handled by a corresponding
executor. Executors integrate with external tools and frameworks, for example the
Metasploit executor can run modules and manage sessions, while the Sliver executor can
generate implants and issue C2 commands. A full list of available executors and their
commands can be found in the :ref:`commands <commands>` reference.

.. note::

   AttackMate executes real attacks and requires intentionally vulnerable or
   dedicated test systems. Never run AttackMate against systems
   you do not own or do not have explicit permission to test.

.. image:: images/attackmate-schema.png
