.. _msf_config:

==========
msf_config
==========

``msf_config`` holds connection settings for the Metasploit RPC daemon (``msfrpcd``).

.. code-block:: yaml

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
