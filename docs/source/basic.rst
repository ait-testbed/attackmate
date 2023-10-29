===========
Basic Usage
===========

AttackMate ships with a executable stub called "attackmate" that can be called like follows:

::

   attackmate -h
   usage: attackmate [-h] --config CONFIG [--debug] [--version]

   AttackMate is an attack orchestration tool that executes full attack-chains based on playbooks.

   options:
     -h, --help       show this help message and exit
     --config CONFIG  Attack-Playbook in yaml-format
     --debug          Enable verbose output
     --version        show program's version number and exit

   (Austrian Institute of Technology) https://aecid.ait.ac.at Version: 0.2.0

Sample Playbook
===============

In our first example we use the following playbook.yml:

.. code-block:: yaml

   vars:
     NMAP: /usr/bin/nmap
     TARGET: localhost
     WEBPORT: 8000

   commands:
     - type: shell
       cmd: $NMAP -sC -p $WEBPORT $TARGET

     - type: regex
       cmd: (\d+)/tcp open   http
       input: RESULT_STDOUT
       output:
         PORT: $MATCH_0

     - type: shell
       cmd: nikto -host $TARGET -port $PORT
       only_if: $PORT == 8000

.. warning::

   For this playbook it is required to have nmap and nikto installed!
   This playbook also needs a webserver at localhost on port 8000.
   You can run ``python3 -mhttp.server`` in a seperate shell to start
   the webserver.


First Run
=========

Now we can run the playbook using the following command:

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

In the **vars**-section we have three variables That can be used later in the **commands**-section.
The nmap-binary is expected at the location */usr/bin/nmap*. The target to attack is *localhost* and
the web-port to attack is *8000*.

::

  vars:
    NMAP: /usr/bin/nmap
    TARGET: localhost
    WEBPORT: 8000

The first command executes an nmap-script-scan on port *8000* at *localhost*. This command illustrates
how to use variables:

::

  commands:
    - type: shell
      cmd: $NMAP -sC -p $WEBPORT $TARGET

As soon as nmap finishes, it automatically stores the output the the built-in variable ``RESULT_STDOUT``.
The regex command executes a regex search using the content of the nmap output. The regular expression is
`(\d+)/tcp open\s+http`. If the expression matches, it will "group" the port number in the variable
``$MATCH_0`` which is a volatile variable and is deleted after the regex-command finishes. In the setting
*output* is a variable defined with the name ``PORT`` and it will be set with the value of ``$MATCH_0``.

::

    - type: regex
      cmd: (\d+)/tcp open\s+http
      input: RESULT_STDOUT
      output:
        PORT: $MATCH_0

The final command is again a shell command that is supposed to execute a nikto scan using the previously
parsed variable ``$PORT``. This command will only be executed if the condition ``$PORT == 8000`` is **True**.

::

    - type: shell
      cmd: nikto -host $TARGET -port $PORT
      only_if: $PORT == 8000
