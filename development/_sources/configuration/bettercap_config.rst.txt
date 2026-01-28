.. _bettercap_config:

================
bettercap_config
================

bettercap_config holds settings for the Bettercap rest-api. The configuration
always starts with an identifier for the connection. This identifier can be
selected when executing a command in a playbook. The first connection in this
file is the default if no explicit connection was selected in the command.

.. code-block:: yaml

   ###
   bettercap_config:
     default:
       url: "http://localhost:8081"
       username: user
       password: password
     remote:
       url: "http://remote.host.tld:8081"
       username: btrcp
       password: somepass

.. code-block:: yaml

   # bettercap-playbook.yml:
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

   This option stores the url to the rest-api

   :type: str

.. confval:: username

   The http basic username for the rest-api

   :type: str

.. confval:: password

   The http basic password for the rest-api

   :type: str

.. confval:: cafile

   The path to the ca-file for the encryption if https is in use.

   :type: str
