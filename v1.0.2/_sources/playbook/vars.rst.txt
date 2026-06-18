.. _variables:

=========
Variables
=========

Variables are defined as key-value pairs in the ``vars`` section and can be used as
placeholders in command settings. Variable names do not require a ``$`` prefix when
defined in the ``vars`` section, but **MUST** be prefixed with ``$`` when referenced
in the ``commands`` section.
If an environment variable with the prefix ``ATTACKMATE_`` exists with the same name,
it will override the playbook variable. For example, the playbook variable ``$FOO`` will
be overwritten by the environment variable ``$ATTACKMATE_FOO``.

.. code-block:: yaml

    vars:
      # the $-sign is optional here:
      $SERVER_ADDRESS: 192.42.0.254
      $NMAP: /usr/bin/nmap

    commands:
      - type: shell
        # the $-sign is required when referencing a variable:
        cmd: $NMAP $SERVER_ADDRESS

.. note::
   Variable substitution uses Python's `string.Template
   <https://docs.python.org/3/library/string.html#string.Template>`_ syntax.

.. note::
   Variables in ``cmd`` settings of a ``loop`` command will be substituted on every
   iteration of the loop, see the :ref:`loop` command for details.


.. _variable-types:

Variable Types and Storage
==========================

All variables are stored internally as plain Python ``str`` values, regardless of
how they were originally defined. Integer values are coerced to strings on ingress —
``set_variable`` explicitly converts ``int`` to ``str`` before storing. This means
that even if a variable is set programmatically to the integer ``42``, it will be
stored and retrieved as the string ``"42"``.

The store holds two separate namespaces:

- **Scalar variables** — simple ``str`` key-value pairs, accessed as ``$varname``.
- **List variables** — ordered sequences of ``str`` values, accessed by index as
  ``$varname[0]``, ``$varname[1]``, etc.

A name cannot be both a scalar and a list simultaneously. Assigning a list value to
an existing scalar name (or vice versa) silently replaces the previous entry.


.. _variable-comparison:

Comparing Variables
===================

When a variable is used in a conditional expression (see :ref:`conditionals`), its
``$`` reference is substituted *before* the expression is evaluated. Because the
store always holds strings, the resolved value will be a ``str`` — even if the
original value looked like a number or a boolean.

This has important consequences depending on the operator used:

**Strings and integers** (``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``, ``is``, ``is not``)
    The resolved variable is always a ``str``. If the right-hand side of the condition
    is written as a bare integer literal (e.g. ``$exit_code == 0``), Python will compare
    a ``str`` against an ``int``. Always use string literals on the right-hand side:

    .. code-block:: yaml

        # Wrong — "0" == 0 is False in Python:
        condition: $exit_code == 0

        # Correct:
        condition: $exit_code == "0"

    Ordering operators (``<``, ``<=``, ``>``, ``>=``) between a ``str`` and an ``int``
    raise a ``TypeError``. If both sides are string literals the comparison uses
    **lexicographic** ordering (``"9" > "10"`` is ``True``), so take care when
    comparing numeric strings.

**Strings and booleans** (``==``, ``!=``)
    In Python, ``bool`` is a subclass of ``int``, so ``True`` equals ``1`` and
    ``False`` equals ``0``. However, a variable set to ``"True"`` or ``"False"``
    is a ``str``, and ``"True" == True`` is ``False`` because the types differ.
    Use string literals for boolean-like flags:

    .. code-block:: yaml

        # Wrong — "True" == True is False:
        condition: $flag == True

        # Correct:
        condition: $flag == "True"

**Identity** (``is``, ``is not``)
    These operators test object identity, not value equality. Because every resolved
    variable is a freshly substituted ``str``, ``$var is "hello"`` is unreliable even
    when the values appear equal. Use ``==`` and ``!=`` for value comparisons; reserve
    ``is`` / ``is not`` for checks between two variables where identity is
    intentionally meaningful.

**Regex** (``=~``, ``!~``)
    Regex conditions bypass ``ast`` parsing entirely and operate directly on the
    substituted string, so type-mismatch issues do not apply. This is the most
    robust operator for testing variable values that may contain numbers, booleans,
    or mixed content:

    .. code-block:: yaml

        condition: $exit_code =~ ^0$

.. seealso::
    `Python reference — Comparisons
    <https://docs.python.org/3/reference/expressions.html#comparisons>`_

    `Python built-in — bool (subclass of int)
    <https://docs.python.org/3/library/functions.html#bool>`_

    `Python ast — Constant node
    <https://docs.python.org/3/library/ast.html#ast.Constant>`_


.. _builtin-variables:

Builtin Variables
=================

The following variables are set automatically by AttackMate during execution:

``RESULT_STDOUT``
    Stores the standard output of the most recently executed command.
    Not set by ``debug``, ``regex``, or ``setvar`` commands.

``RESULT_CODE``
    Stores the return code of the most recently executed command.

``LAST_MSF_SESSION``
    Set whenever a new Metasploit session is created. Contains the session number.

``LAST_SLIVER_IMPLANT``
    Set whenever a new Sliver implant is generated. Contains the path to the implant file.

``LAST_FATHER_PATH``
    Set whenever a Father rootkit is generated. Contains the path to the rootkit.

``REGEX_MATCHES_LIST``
    Set every time a regex command yields matches. Contains a list of all matches.
    If ``sub`` or ``split`` finds no match, the original input string is returned.
