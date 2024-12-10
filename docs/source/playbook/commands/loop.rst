====
loop
====

Execute a set of commands in a loop, based on a condition or iteration over a list of values.

The `loop` command allows dynamic iteration over lists or ranges of values, executing a sequence of commands for each iteration. It provides flexibility when working with variable data such as network scans, enabling the execution of different commands depending on the results, without prior knowledge of the number of iterations.

.. note::

   The loop command works with two primary loop conditions: iterating over a list of values (`items`) or iterating over a numerical range (`range`).

.. code-block:: yaml

   vars:
     LISTA:
       - one
       - two

   commands:
     - type: loop
       cmd: "items(LISTA)"
       commands:
         - type: shell
           cmd: echo hello
         - type: debug
           cmd: $LOOP_ITEM

     - type: loop
       cmd: "range(0, 3)"
       commands:
         - type: shell
           cmd: echo "Index $LOOP_INDEX"
         - type: debug
           cmd: $LOOP_INDEX

**Loop with items**:
This mode iterates over the elements of a list and substitutes each element into the commands.
The current item is accessible as the `$LOOP_ITEM` variable.

**Loop with range**:
This mode iterates over a range of integers. The current index is accessible as the `$LOOP_INDEX` variable.

**Loop until condition is fulfilled**
This mode iterates indefinitely until the condition is fulfilled. (Checked before every command within the loop)
Variables in cmd settings of an until loop command until($VAR1 == $VAR2) will be substituted from the variable store on every iteration of the loop.
The current index/iteration of the loop is also accessible as the `$LOOP_INDEX` variable for the until() condition.

.. confval:: cmd

   The loop condition. This defines how the loop should iterate, either over a list or a range of values, or idefinitely until the
   condition defined in until() is rached.

   :type: str
   :required: ``True``

   Examples:

   - **items(LISTA)**: Iterate over the elements of a list named `LISTA`.
   - **range(0, 10)**: Iterate over a range from 0 to 9.
   - **until($PORT == 7)

.. confval:: break_if

   If defined, this condition is checked before every command in the loop.
   If the condition evaluates to `True`, break out of the loop.
   Supports the same operators like :confval:`only_if`.

   :type: str
   :required: ``False``

.. confval:: commands

   The list of commands to execute during each iteration of the loop. These commands are executed once per iteration, with loop-specific variables (`$LOOP_ITEM` or `$LOOP_INDEX`) available for substitution.

   :type: list[Command]
   :required: ``True``

   .. code-block:: yaml

      vars:
        LISTA:
          - port1
          - port2

      commands:
        - type: loop
          cmd: "items(LISTA)"
          commands:
            - type: shell
              cmd: "nmap -p $LOOP_ITEM 10.10.10.10"
            - type: debug
              cmd: $LOOP_ITEM

   In the above example, each element of `LISTA` (port1, port2) is substituted into the loop, and an Nmap scan is run for each port.

   Example of looping over a range:

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

.. confval:: LOOP_ITEM

   In `items` loops, this variable holds the current item from the list being iterated over.

   :type: str

.. confval:: LOOP_INDEX

   In `range` loops, this variable holds the current index of the iteration.

   :type: int
