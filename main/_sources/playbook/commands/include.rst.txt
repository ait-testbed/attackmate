=======
include
=======

Include and run commands from another yaml-file.

.. code-block:: yaml

      # main.yml:
      vars:
        FOO: "hello world"
      commands:
        - type: debug
          cmd: Loading commands from another file

        - type: include
          local_path: do_work.yml

        - type: debug
          cmd: Finished run from another file


      # do_work.yml:
      commands:
        - type: debug
          cmd: $FOO

.. confval:: local_path

   Path to the yaml-file

   :type: str
   :required: ``True``
