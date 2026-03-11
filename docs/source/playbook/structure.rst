=========
Structure
=========

AttackMate playbooks must be written in valid `YAML-format <https://yaml.org/>`_ and require at least a :ref:`commands section <commands>`:

.. code-block:: yaml

   commands:
     - type: shell
       cmd: nmap www.vulnerable-system.tld
     - type: shell
       cmd: nikto -host www.vulnerable-system.tld

Usually playbooks also contain a :ref:`vars <variables>` section to define reusable
placeholders that can be referenced throughout the ``commands`` section:

.. code-block:: yaml

   vars:
     TARGET: www.vulnerable-system.tld
     NMAP: /usr/bin/nmap
     NIKTO: /usr/bin/nikto


   commands:
     - type: shell
       cmd: $NMAP -T4 $TARGET
     - type: shell
       cmd: $NIKTO -host $TARGET
