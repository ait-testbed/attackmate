======
father
======

The Fahter LD_PRELOAD rootkit requires to compile the config settings into the binary.
This command compiles the binary and stores the path in the variable ``LAST_FATHER_PATH``.
If ``local_path`` is not defined, the command will create a temporary directory and copy
the sources into the directory before compiling the rootkit.


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
