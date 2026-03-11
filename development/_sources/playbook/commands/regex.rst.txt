=====
regex
=====

Parse and transform variables using regular expressions. For more information
about regular expressions and regex syntax see `Python Regex  <https://docs.python.org/3/library/re.html>`_.

.. note::

   This command does not modify ``RESULT_STDOUT``.


The following example extracts a port number from the output of a shell command and stores it in the variable ``UNREALPORT``:

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


Using ``mode: split``, a string can be tokenized by a delimiter, in this case, whitespace ``"\ +"``:

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

.. confval:: cmd

   The regular expression pattern to apply.

   :type: str
   :required: True

.. confval:: mode

  The Python regex function to use. One of:

   * ``findall`` - find all non-overlapping matches
   * ``search`` - find the first match anywhere in the string
   * ``split`` - split the string by occurrences of the pattern
   * ``sub`` - replace occurrences of the pattern with :confval:`replace`

  :type: str
  :default: ``findall``
  :required: False

.. confval:: replace

  This variable must be set for ``mode: sub``. It holds the replacement-string for the substitution.

  :type: str
  :default: ``None``
  :required: when ``mode: sub``

   .. code-block:: yaml

      commands:
        - type: setvar
          cmd: "hello world"
          variable: FOO

        - type: regex
          cmd: hello
          replace: whaat
          mode: sub
          input: FOO
          output:
            BAR: $MATCH_0

        - type: debug
          cmd: $BAR


.. confval:: input

   Name of the variable whose value will be used as the regex input
   (without the leading ``$``).

   :type: str
   :default: ``RESULT_STDOUT``
   :required: False

.. confval:: output

   Mapping of variable names to match references (e.g. ``MYVAR: $MATCH_0``).

   :type: dict[str,str]
   :required: True

   Matches are indexed as ``$MATCH_0``, ``$MATCH_1``, etc. For nested results
   (lists of tuples), matches are indexed as ``$MATCH_0_0``, ``$MATCH_0_1``, etc.

   If the pattern does not match, no output variables are set. If ``sub`` or
   ``split`` find no match, the original input string is returned.

   The :ref:`builtin variables <builtin-variables>` ``REGEX_MATCHES_LIST`` is also populated with a list of
   all matches whenever the command produces results.


   .. note::

       Running AttackMate in debug mode (--debug) prints a full dump of all matches.
