.. _bettercap_config:

================
bettercap_config
================

``bettercap_config`` holds connection profiles for the Bettercap REST API. Each profile
is identified by a user-defined name that can be referenced in playbook commands via the
``connection`` field. If no connection is specified, the first profile in the configuration
is used as the default.

.. code-block:: yaml

   bettercap_config:
     default:
       url: "http://localhost:8081"
       username: user
       password: password
     remote:
       url: "http://remote.host.tld:8081"
       username: btrcp
       password: somepass



The following playbook example shows how to target a specific connection, and how the
default connection is used when none is specified:

.. code-block:: yaml

   commands:
     # this is executed on the remote host:
     - type: bettercap
       cmd: post_api_session
       data:
         cmd: "net.sniff on"
       connection: remote
     # this is executed on localhost:
     - type: bettercap
       cmd: get_events


.. confval:: url

   URL of the Bettercap REST API.

   :type: str

.. confval:: username

   HTTP Basic Auth username for the Bettercap REST API.

   :type: str

.. confval:: password

   HTTP Basic Auth password for the Bettercap REST API.

   :type: str

.. confval:: cafile

   Path to the CA certificate file used for TLS verification when connecting via HTTPS.

   :type: str
