====
json
====

Parse variables from an .json file or from a variable (for example ``RESULT_STDOUT``) that is a valid json string.


.. code-block:: yaml

    commands:
      - type: json
        cmd: "/path/to/samplefile.json"
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

.. confval:: cmd

   Json input to parse from. Valid inputs are a path to a json file or, if use_var is TRUE, the variable name from the variable store (without the $)

   :type: str
   :required: ``True``

.. confval:: varstore

   If True logs the variable store before and afteradding variables with json command.

   :type: bool
   :required: ``False``

.. confval:: use_var

   parse from a variable store variable instead of from a json file.

   :type: bool
   :required: ``False``
