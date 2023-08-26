.. _msf-session:

===========
msf-session
===========

This command allowes to read and write commands to (Meterpreter)sessions that
have previously created by msf-modules(see :ref:`msf-module`).


.. note::

   To configure the connection to the msfrpc-server see :ref:`msf_config`

.. confval:: stdapi

   Load stdapi module in the Meterpreter-session.

   :type: bool
   :default: ``False``

.. confval:: write

   Execute a raw write-operation without reading the output.

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
