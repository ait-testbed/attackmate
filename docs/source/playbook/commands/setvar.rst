======
setvar
======

Set a variable to a string value. Useful for string interpolation and copying or
transforming existing variables.

.. note::

   This command does not modify ``RESULT_STDOUT``.

.. code-block:: yaml

   vars:
     FOO: "WORLD"

   commands:
     - type: setvar
       cmd: HELLO $FOO
       variable: BAR

.. confval:: variable

   Name of the variable to set (without the leading ``$``).

   :type: str
   :required: True


.. confval:: cmd

   The value to assign to the variable. Supports variable substitution.

   :type: str
   :required: True

.. confval:: encoder

   Encode or decode the value of ``cmd`` before storing it in ``variable``.

   Supported values:

   * ``base64-encoder`` — encode to Base64
   * ``base64-decoder`` — decode from Base64
   * ``rot13`` — apply ROT13
   * ``urlencoder`` — percent-encode for use in URLs
   * ``urldecoder`` — decode percent-encoded strings

   :type: str['base64-encoder', 'base64-decoder', 'rot13', 'urlencoder', 'urldecoder']

   .. note::

      Note that if encoding fails, the plain value is stored and a warning is printed.

   Example:

   .. code-block:: yaml

      commands:
        - type: setvar
          variable: TEST
          cmd: Hello World
          encoder: base64-encoder

        - type: debug
          cmd: $TEST

        - type: setvar
          variable: TEST
          cmd: $TEST
          encoder: base64-decoder

        - type: debug
          cmd: $TEST

        - type: setvar
          variable: TEST
          cmd: $TEST
          encoder: rot13

        - type: debug
          cmd: $TEST

        - type: setvar
          variable: TEST
          cmd: $TEST
          encoder: rot13

        - type: debug
          cmd: $TEST

        - type: setvar
          variable: TEST
          cmd: $TEST
          encoder: urlencoder

        - type: debug
          cmd: $TEST

        - type: setvar
          variable: TEST
          cmd: $TEST
          encoder: urldecoder

        - type: debug
          cmd: $TEST

        - type: setvar
          variable: TEST
          cmd: $TEST
          encoder: base64-decoder

        - type: debug
          cmd: $TEST
