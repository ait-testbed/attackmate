.. _loop:

====
loop
====

Execute a sequence of commands repeatedly, either by iterating over a list of values, a numerical range, or until a condition is met.

This is useful when the number of iterations is not known in advance, for example, when processing results from a network scan.

.. note::

   The loop command works with two primary loop conditions: iterating over a list of values (``items()``) or iterating over a numerical range (``range()``).

.. code-block:: yaml

   vars:
     LISTA:
       - one
       - two

   commands:
     # Iterate over a list:
     - type: loop
       cmd: "items(LISTA)"
       commands:
         - type: shell
           cmd: echo hello
         - type: debug
           cmd: $LOOP_ITEM

     # Iterate over a range:
     - type: loop
       cmd: "range(0, 3)"
       commands:
         - type: shell
           cmd: echo "Index $LOOP_INDEX"
         - type: debug
           cmd: $LOOP_INDEX


Loop Modes
----------

**items(LIST)**:
Iterates over the elements of a list and substitutes each element into the commands.
The current item is accessible as the ``$LOOP_ITEM`` variable.

**range(start, end)**
Iterates over a range of integers ``start`` (inclusive) to ``end`` (exclusive). The current index is accessible as the ``$LOOP_INDEX`` variable.

**until(condition)**
Iterates indefinitely until the condition is evaluates to ``True``, checked before every command in the loop body.
Variables in cmd section of an until loop command until(``$VAR1 == $VAR2``) will be substituted from the variable store on every iteration of the loop.
The current iteration count is available as ``$LOOP_INDEX``.

Example: ``until($PORT == 7)``

Configuration
-------------

.. confval:: cmd

   The loop condition. Defines how the loop iterates, either over a list or a range of values, or idefinitely until the
   condition defined in ``until()`` is met.

   :type: str
   :required: True

   Examples:

   - **items(LISTA)**: Iterate over the elements of a list named ``LISTA``.
   - **range(0, 10)**: Iterate over a range from 0 to 9.
   - **until($PORT == 7)**: Iterate until the condition is met

.. confval:: break_if

   A condition checked before every command in the loop.
   If it evaluates to `True`, the loop exits immediately
   Supports the same operators as :confval:`only_if`.

   :type: str
   :required: False

.. confval:: commands

   The list of commands to execute during each iteration of the loop. These commands are executed once per iteration, with loop-specific variables (``$LOOP_ITEM`` or ``$LOOP_INDEX``) available for substitution within these commands.

   :type: list[Command]
   :required: True


Loop Variables
--------------

.. confval:: LOOP_ITEM

   In `items` loops, this variable holds the current item from the list being iterated over.

   :type: str

.. confval:: LOOP_INDEX

   In `range` loops, this variable holds the current index of the iteration.

   :type: int


Examples
--------


Iterate over a list and run an Nmap scan for each element:

   .. code-block:: yaml

      vars:
        PORTS:
          - port1
          - port2

      commands:
        - type: loop
          cmd: "items(PORTS)"
          commands:
            - type: shell
              cmd: "nmap -p $LOOP_ITEM 10.10.10.10"
            - type: debug
              cmd: $LOOP_ITEM


Iterate over a range using variables for start and end:

   .. code-block:: yaml

      vars:
        INDEX_START: 0
        INDEX_END: 5

      commands:
        - type: loop
          cmd: "range($INDEX_START, $INDEX_END)"
          commands:
            - type: shell
              cmd: echo "Index is $LOOP_INDEX"
