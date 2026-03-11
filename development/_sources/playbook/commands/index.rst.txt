.. _commands:

========
Commands
========

The ``commands:`` section of a playbook holds a list of AttackMate commands that are executed sequentially from
top to bottom.

Every command, regardless of its type supports the following general options:

.. confval:: cmd

   The command that should be executed. The meaning of this option varies depending on the type of command.

   :type: str

.. confval:: save

   Save the output of the command to a file.

   :type: str

   .. code-block:: yaml

      commands:
        - type: shell
          cmd: nmap localhost
          save: /tmp/nmap_localhost.txt

.. confval:: exit_on_error

   Attackmate will exit with an error if the command returns a non-zero exit code.

   :type: bool
   :default: ``True``

.. confval:: error_if

   Raise an error if the given pattern is found in the command output.

   :type: str(regex)

   .. code-block:: yaml

      commands:
        # throws an error
        - type: http-client
          cmd: get
          url: https://www.bing.com
          error_if: ".*bing.*"


.. confval:: error_if_not

   Raise an error if the given pattern is **not** found in the command output.

   :type: str(regex)

   .. code-block:: yaml

      commands:
        # throws an error
        - type: http-client
          cmd: get
          url: https://www.google.com
          error_if_not: ".*bing.*"


.. confval:: loop_if

   Re-execute the command if the given pattern is found in the output. Repeats
   until the pattern no longer matches or ``loop_count`` is reached.

   :type: str(regex)

   .. code-block:: yaml

      commands:
        # loop until max-loop-count reached:
        - type: http-client
          cmd: get
          url: https://www.google.com
          loop_if_not: ".*google.*"


.. confval:: loop_if_not

   Re-execute the command if the given pattern is **not** found in the output. Repeats
   until the pattern matches or ``loop_count`` is reached.

   :type: str(regex)

   .. code-block:: yaml

      commands:
        # loop until max-loop-count reached:
        - type: http-client
          cmd: get
          url: https://www.google.com
          loop_if_not: ".*bing.*"

.. confval:: loop_count

      Maximum number of repetitions when ``loop_if* or ``loop_if_not`` is set.

   :type: int
   :default: ``3``

.. confval:: only_if

   Execute this command only if the condition evaluates to ``True``. Supported operators:

   * ``var1 == var2``, ``var1 != var2``
   * ``var1 is var2``, ``var1 is not var2``
   * ``var1 < var2``, ``var1 <= var2``, ``var1 > var2``, ``var1 >= var2``
   * ``string =~ pattern`` — matches if string satisfies the regex pattern
   * ``string !~ pattern`` — matches if string does not satisfy the regex pattern
   * ``not var``, ``var``, ``None``

   :type: str(condition)

   .. note::

      The ``=~`` operator is used to check if a string matches a regular expression pattern.
      The ``!~`` operator is used to check if a string does **not** match a regular expression pattern.

   .. code-block:: yaml

      commands:
        # Get the PID of the running mysqld process:
        - type: shell
          cmd: pgrep mysqld

        # Extract the first captured group from the output, splitting on newlines.
        # Stores the result in $KILLPID via the MATCH_0 capture variable:
        - type: regex
          mode: split
          cmd: "\n"
          output:
            KILLPID: $MATCH_0

        # Only kill if it is not the init process with PID 1:
        - type: shell
          cmd: kill $KILLPID
          only_if: $KILLPID > 1

        # Only execute if the regex pattern matches:
        - type: shell
          cmd: echo "regex match found"
          only_if: some_string =~ some[_]?string

   .. warning::

        When comparing strings with integers, standard Python conventions apply:

        **Equality / Inequality** (``==``, ``!=``):
        A string and an integer are never equal, so ``"1" == 1`` is ``False``
        and ``"1" != 1`` is ``True``.

        **Identity** (``is``, ``is not``):
        Compares object identity, not value. ``"1" is 1`` is always ``False``
        because a string and an integer are distinct objects, regardless of
        their apparent values.

        **Ordering** (``<``, ``<=``, ``>``, ``>=``):
        Comparing a string with an integer raises a ``TypeError`` in Python 3
        since the two types have no defined ordering. These operators should
        only be used when both operands share the same type.

        **Integers and Booleans** (``==``, ``!=``):
        In Python, ``bool`` is a subclass of ``int``, so ``1 == True`` and
        ``0 == False`` are both ``True``, while any other integer (e.g.
        ``2 == True``) is ``False``.  This also means that if a
        ``$variable`` has been set to the string ``"True"`` or ``"False"``,
        comparing it against a boolean literal (``$var == True``) will
        always yield ``False`` — because the resolved value is a ``str``
        while the literal is parsed as a ``bool`` by ``ast``.  Use string
        literals for boolean-like flags stored in the ``VariableStore``:
        ``$flag == "True"``.

        Importantly, before a condition is evaluated, all ``$variable`` references are
        resolved by the ``VariableStore``.  **The store holds every value as a
        plain Python** ``str``, even values that were originally integers
        are coerced to ``str`` on ingress.

.. confval:: background

   Execute the command as a background subprocess. When enabled, output is not printed
   and ``error_if`` / ``error_if_not`` have no effect.

   :type: bool
   :default: ``False``

   .. note::

      The command in background-mode will change the :ref:`builtin variables <builtin-variables>`
      ``RESULT_STDOUT`` to "Command started in Background" and ``RESULT_CODE`` to 0.

   Background mode is not supported for

   * MsfModuleCommand
   * IncludeCommand
   * VncCommand
   * BrowserCommand

   Background mode together with a session is not supported for the following commands:

   * SSHCommand
   * SFTPCommand





.. confval:: kill_on_exit

   If this command runs in background mode, the option ``kill_on_exit`` controls
   whether the main process kills the subprocess on exit (``True``) or waits for it to finish (``False``).

   :type: bool
   :default: ``True``

.. confval:: metadata

   An optional dictionary of key-value pairs that are logged alongside the command
   but have no effect on execution.

   :type: Dict
   :default: None

   .. code-block:: yaml

      commands:
        - type: debug
          cmd: Come on, Cat
          metadata:
            version: 1
            author: Ellen Ripley


The next pages will describe each command type in detail.

.. toctree::
   :maxdepth: 4
   :hidden:

   bettercap
   browser
   debug
   father
   httpclient
   include
   json
   loop
   mktemp
   msf-module
   msf-session
   payload
   regex
   remote
   setvar
   shell
   sftp
   sleep
   sliver
   sliver-session
   ssh
   vnc
   webserv
