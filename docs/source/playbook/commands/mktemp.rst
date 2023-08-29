======
mktemp
======

Create temporary files or directories that are deleted when the programm exits.
The path to the file or directory is storen in a given variable.

.. code-block:: yaml

   ###
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

   Define if a file or directory will be created. Valid
   options are: *file* or *dir*.

   :type: str
   :default: ``file``


.. confval:: variable

   This setting defines a variable where the path of the
   temporary file or directory will be stored.

   :type: str
   :required: ``True``
