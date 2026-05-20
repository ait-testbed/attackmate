======
mktemp
======

Create a temporary file or directory that is automatically deleted when AttackMate exits.
The path to the file or directory is stored in a variable for use in subsequent
commands.

.. code-block:: yaml

   commands:
     - type: mktemp
       cmd: file
       variable: SOMEFILE

     - type: debug
       cmd: "$SOMEFILE"

     - type: mktemp
       cmd: dir
       variable: TEMPDIR

     - type: debug
       cmd: "$TEMPDIR"


.. confval:: cmd

   Whether to create a temporary file or directory.

   :type: str
   :default: ``file``

   Valid values:

   * ``file`` — create a temporary file
   * ``dir`` — create a temporary directory


.. confval:: variable

   Name of the variable where the path of the
   temporary file or directory will be stored (without the leading ``$``).

   :type: str
   :required: True
