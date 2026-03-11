===========
Basic Usage
===========

AttackMate is invoked via the ``attackmate`` command:

::

   attackmate -h
   usage: attackmate [-h] --config CONFIG [--debug] [--version] [--json] [--append_logs]

   AttackMate is an attack orchestration tool that executes full attack-chains based on playbooks.

   options:
     -h, --help       show this help message and exit
     --config CONFIG  Attack-Playbook in yaml-format
     --debug          Enable verbose output
     --version        show program's version number and exit
     --json           log commands to attackmate.json
     --append_logs    append logs to attackmate.log, output.log and attackmate.json instead of overwriting

   (Austrian Institute of Technology) https://aecid.ait.ac.at Version: 0.2.0

Sample Playbook
===============

The following playbook demonstrates a simple reconnaissance chain using nmap, regex parsing,
and a conditional nikto scan:

.. code-block:: yaml

   vars:
     NMAP: /usr/bin/nmap
     TARGET: localhost
     WEBPORT: "8000"

   commands:
     - type: shell
       cmd: $NMAP -sC -p $WEBPORT $TARGET

     - type: regex
       cmd: (\d+)/tcp open\s+http
       input: RESULT_STDOUT
       output:
         PORT: $MATCH_0

     - type: shell
       cmd: nikto -host $TARGET -port $PORT
       only_if: $PORT == 8000

.. note::

   This playbook requires ``nmap`` and ``nikto`` to be installed, and a web server
   running on ``localhost:8000``. You can start one with:

   ::

      $ python3 -mhttp.server


First Run
=========

Run the playbook with ``--debug`` for verbose output:

::

   $ attackmate --debug playbook.yml

.. note::

   The playbook path can be absolute, relative to the current working directory,
   or relative to ``/etc/attackmate/playbooks``.

Expected output:

::

  $ attackmate --debug playbook.yml
    2023-09-24 20:17:36 DEBUG   | No config-file found. Using empty default-config
    2023-09-24 20:17:36 DEBUG   | Template-Command: '$NMAP -sC -p $WEBPORT $TARGET'
    2023-09-24 20:17:36 INFO    | Executing Shell-Command: '/usr/bin/nmap -sC -p 8000 localhost'
    2023-09-24 20:17:37 DEBUG   | Template-Command: '(\d+)/tcp open\s+http'
    2023-09-24 20:17:37 WARNING | RegEx: '(\d+)/tcp open\s+http'
    2023-09-24 20:17:37 DEBUG   | {'MATCH_0': '8000'}
    2023-09-24 20:17:37 DEBUG   | Template-Command: 'nikto -host $TARGET -port $PORT'
    2023-09-24 20:17:37 INFO    | Executing Shell-Command: 'nikto -host localhost -port 8000'

Explanation
===========

**vars** defines reusable variables that can be referenced throughout the ``commands`` section via ``$VARNAME`` substitution.
In this example, we define the path to the nmap binary, the target host, and the web port to attack.
The nmap-binary is expected at the location */usr/bin/nmap*, the target to attack is *localhost* and
the web-port to attack is *8000*.

.. code-block:: yaml

  vars:
    NMAP: /usr/bin/nmap
    TARGET: localhost
    WEBPORT: "8000"

The first command executes an nmap script scan on port *8000* against the target *localhost*. This command illustrates
how to use variables: Variables are substituted at runtime using ``$VARNAME`` syntax:

.. code-block:: yaml

  commands:
    - type: shell
      cmd: $NMAP -sC -p $WEBPORT $TARGET

As soon as nmap finishes, its output is automatically stored in the built-in variable ``RESULT_STDOUT``.
The regex command searches this output using the expression ``(\d+)/tcp open\s+http``.
If it matches, the captured port number is stored in the volatile variable ``$MATCH_0`` (deleted after the regex-command finishes),
which is then assigned to the persistent variable ``PORT`` via the ``output`` mapping:

.. code-block:: yaml

    - type: regex
      cmd: (\d+)/tcp open\s+http
      input: RESULT_STDOUT
      output:
        PORT: $MATCH_0

The final command is a shell command that executes a nikto scan using the previously
parsed ``$PORT`` variable. The  ``only_if`` condition ensures this command will only be executed if ``$PORT == 8000`` is **True**.

.. code-block:: yaml

    - type: shell
      cmd: nikto -host $TARGET -port $PORT
      only_if: $PORT == 8000
