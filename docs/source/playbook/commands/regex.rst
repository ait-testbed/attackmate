=====
regex
=====

This command parses variables using regular expressions. For more information
about regular expressions see `Python Regex  <https://docs.python.org/3/library/re.html>`_


.. confval:: mode

   Specifies the python regex-function. One of: ``search``, ``split`` or ``findall``.

   :type: str
   :default: ``findall``

.. confval:: input

   Parse the value of this variable.

   :type: str
   :default: ``RESULT_STDOUT``

.. confval:: output

   Defines where to store the results of the regular expression. This
   must be a list of key-value pairs("variable-name": "$MATCH"). The matches
   of the regular expressions are stored in temporary variables $MATCH. If the
   match is stored in a list or in a list of tuples the variablename will be
   numbered by the index. For examle: "$MATCH_0_0" for the first element in the
   first occurance.

   .. note::

       A dump containing all matches will be printed if penpal runs in debug-mode.

   :type: dict[str,str]
   :required: True

   The following example parses the portnumber from the output of the last command and stores it in variable "UNREALPORT":

   .. code-block:: yaml

      commands:
        - type: shell
          cmd: echo "6667/tcp open  irc UnrealIRCd"

        - type: regex
          cmd: (\d+).*UnrealIRCd
          output:
              UNREALPORT: "$MATCH_0"

        - type: debug
          cmd: "Port: $UNREALPORT"


   By using the mode "split", strings that are seperated by whitespaces can be tokenized:

   .. code-block:: yaml

      commands:
        - type: shell
          cmd: echo "6667/tcp open  irc UnrealIRCd"

        - type: regex
          cmd: "\ +"
          mode: split
          output:
              # {'MATCH_0': '6667/tcp', 'MATCH_1': 'open', 'MATCH_2': 'irc', 'MATCH_3': 'UnrealIRCd\n'}
              UNREALPORT: "$MATCH_0"

        - type: debug
          cmd: "Port: $UNREALPORT"
