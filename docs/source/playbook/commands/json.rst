====
json
====

Parse variables from an .json file or from a variable (for example ``RESULT_STDOUT``) that is a valid json string.
If the "local_path" option is used, read the json from this command. "cmd" option is optional.
If "local_path" is defined, "cmd" will be ignored.
If no "local_path" is set, read the json from "cmd"


.. code-block:: yaml

    commands:
      - type: json
        local_path: "/path/to/samplefile.json"
        varstore: True
      - type: shell
        cmd: |
          cat <<EOF
          {
            "name": "Whiskers",
            "favorite_toys": ["ball", "feather", "laser pointer"]
          }
          EOF
      - type: json
        cmd: RESULT_STDOUT
        use_var: True


.. confval:: local_path

   Json input to parse from. Valid input is a path to a json file. If "local_path" is set, "cmd" will be ignored.

   :type: str
   :required: ``False``

.. confval:: cmd

   Json input to parse from. Valid input is a variable name from the variable store (without the leading $), that contains a valid json string.

   :type: str
   :required: ``False``

Either local_path OR cmd is required

.. confval:: varstore

   If True logs the variable store before and afteradding variables with json command.

   :type: bool
   :required: ``False``
