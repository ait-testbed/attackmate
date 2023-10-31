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

   :type: str['base64-encoder', 'base64-decoder', 'rot13', 'urlencoder', 'urldecoder']
