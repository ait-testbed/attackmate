======
setvar
======

Set a variable. This could be used for string interpolation or for
copying variables.

.. code-block:: yaml

   ###
   vars:
     FOO: "WORLD"

   commands:
     - type: setvar
       cmd: HELLO $FOO
       variable: BAR

.. confval:: variable

   The variable-name that stores the value of *cmd*

   :type: str
   :required: ``True``


.. confval:: cmd

   The value of the variable

   :type: str
   :required: ``True``

.. confval:: encoder

   If encoder is set, the command in cmd will be encoded before stored in ``variable``.
   Please note that if encoding fails, this command will fallback to plain cmd and will
   print out a warning.

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


   :type: str['base64-encoder', 'base64-decoder', 'rot13', 'urlencoder', 'urldecoder']
