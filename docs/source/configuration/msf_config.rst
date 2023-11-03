.. _msf_config:

==========
msf_config
==========

msf_config holds settings for the Metasploit modules and sessions.
Most of these settings control the Metsaploit RPC connection.

.. code-block:: yaml

   ###
   msf_config:
     password: securepassword
     server: 10.18.3.86

.. confval:: server

   This option stores the servername or ip-address of the msfrpcd

   :type: str
   :default: 127.0.0.1


.. confval:: password

   This option stores the password of the rpc-connection.

   :type: str
   :default: None


.. confval:: ssl

   This option enables encryption for the rpc-connection

   :type: bool
   :default: True


.. confval:: port

   This option sets the port for the rpc-connection.

   :type: int
   :default: 55553


.. confval:: uri

   This option sets uri of the rpc-api.
