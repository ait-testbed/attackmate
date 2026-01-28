======
father
======

The Fahter LD_PRELOAD rootkit requires to compile the config settings into the binary.
This command compiles the binary and stores the path in the variable ``LAST_FATHER_PATH``.
If ``local_path`` is not defined, the command will create a temporary directory and copy
the sources into the directory before compiling the rootkit.

Father can be found at `this GitHub-Page <https://github.com/mav8557/Father>`_


.. code-block:: yaml

   ###
   commands:
     - type: father
       cmd: generate
       hiddenport: 2222
       shell_pass: "superpass"
       env_var: "norkt"

     - type: debug
       cmd: ""
       varstore: True
     # {'LAST_FATHER_PATH': '/tmp/tmpuou9rb0a/Father/rk.so', 'RESULT_STDOUT': 'Saved to /tmp/tmpuou9rb0a/Father/rk.so', 'RESULT_RETURNCODE': '0'}

.. confval:: gid

   The group id under which the rootkit will operate. All processes of this gid will be hidden.

   :type: int
   :default: ``1337``

.. confval:: srcport

   The magic port number that allows to connect to the accept-backdoor of father.

   :type: int
   :default: ``54321``

.. confval:: epochtime

   Time for timebomb() to go off, in seconds since 1970-01-01

   :type: int
   :default: ``0000000000``

.. confval:: env_var

   Magic environment variable for Local Privilege Escalation (LPE). If this environment
   variable is set, it is possible to escalate privileges using *sudo* or *gpasswd*

   :type: str
   :default: ``lobster``

.. confval:: file_prefix

   Magic prefix for hidden files.

   :type: str
   :default: ``lobster``

.. confval:: preload_file

   Hide this preload file(hide the rootkit)

   :type: str
   :default: ``ld.so.preload``

.. confval:: hiddenport

   Port to remove from netstat output, etc

   :type: str(hex)
   :default: ``D431``

.. confval:: shell_pass

   Password for accept() backdoor shell

   :type: str
   :default: ``lobster``

.. confval:: install_path

   Location of rootkit on disk

   :type: str
   :default: ``/lib/selinux.so.3``

.. confval:: local_path

   Copy the rootkit to this local path before compiling it.
   If not set, the builder will generate a temporary path.

   :type: str

.. confval:: arch

   Target arch to compile the rootkit to. Currently only amd64
   is supported.

   :type: str
   :default: ``amd64``

.. confval:: build_command

   Use this command to build the rootkit. This setting might be useful
   for compiling the rootkit in a chroot-environment.

   :type: str
   :default: ``make``
