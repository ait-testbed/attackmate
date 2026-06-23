.. _msf_config:

==========
msf_config
==========

``msf_config`` holds connection settings for one or more Metasploit RPC daemon (``msfrpcd``)
instances. Each connection is identified by a name. The first defined connection is used by
default when a command does not specify one explicitly.

.. code-block:: yaml

   msf_config:
     primary:
       password: securepassword
       server: 10.18.3.86

Multiple servers can be defined and selected per command via the :confval:`connection` field:

.. code-block:: yaml

   msf_config:
     server1:
       password: securepassword
       server: 10.18.3.86
     server2:
       password: anothersecret
       server: 10.18.3.87

.. note::

   **Backwards compatibility:** The legacy single-server format is still accepted and is
   automatically migrated to a named entry called ``default``:

   .. code-block:: yaml

      # Legacy format (still supported)
      msf_config:
        password: securepassword
        server: 10.18.3.86


.. confval:: server

   The servername or IP address of the ``msfrpcd``.

   :type: str
   :default: 127.0.0.1


.. confval:: port

   Port on which ``msfrpcd`` is listening.

   :type: int
   :default: 55553


.. confval:: uri

   URI of the RPC API.


.. confval:: ssl

   Enables encryption for the RPC connection.

   :type: bool
   ::default: ``True``


.. confval:: password

   The password for the RPC connection.

   :type: str
   :default: None
