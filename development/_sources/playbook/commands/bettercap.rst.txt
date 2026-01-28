.. _bettercap:

=========
bettercap
=========

This command communicates with the bettercap rest-api. It supports all
endpoints of the official api. Please see `Bettercap Rest-Api Docs  <https://www.bettercap.org/modules/core/apirest/>`_
for additional information. All commands return a json-formatted string.

All commands support the setting: `connection`. This settings allows to query a api-command on a specific host. The name
of the connection must be set in attackmate.yml. If connection is not set, the command will be executed on the first
connection in attackmate.yml:

.. code-block:: yaml

   # .attackmate.yml:
   bettercap_config:
     default:
       url: "http://localhost:8081"
       username: btrcp
       password: secret
     remote:
       url: "http://somehost:8081"
       username: user
       password: secret

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

.. note::

   To configure the connection to the bettercap rest-api see :ref:`bettercap_config`


post_api_session
----------------

Post a command to the interactive session.

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: post_api_session
       data:
         cmd: "net.sniff on"

.. confval:: data

   Dict(key/values) of post-data:

   :type: Dict[str,str]

get_file
--------

Get a file from the api-server.

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_file
       filename: "/etc/passwd"

.. confval:: filename

   Full path of the filename on the api-server.

   :type: str


delete_api_events
-----------------

Clear the events buffer.

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: delete_api_events


get_events
----------

Get all events

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_events


get_session_modules
-------------------

Get session modules

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_modules

get_session_env
---------------

Get session environment

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_env

get_session_gateway
-------------------

Get session gateway

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_gateway

get_session_interface
---------------------

Get session interface

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_interface

get_session_options
-------------------

Get session options

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_options

get_session_packets
-------------------

Get session packets

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_packets

get_session_started_at
----------------------

Get session started at

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_started_at

get_session_hid
---------------

Get a JSON of the HID devices in the current session

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_hid

.. confval:: mac

   Optional parameter to return the info of a specific endpoint

   :type: str

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_hid
       mac: "32:26:9f:a4:08"

get_session_ble
---------------

Get a JSON of the BLE devices in the current session.

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_ble

.. confval:: mac

   Optional parameter to return the info of a specific endpoint

   :type: str

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_ble
       mac: "32:26:9f:a4:08"

get_session_lan
---------------

Get a JSON of the lan devices in the current session

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_lan

.. confval:: mac

   Optional parameter to return the info of a specific endpoint

   :type: str

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_lan
       mac: "32:26:9f:a4:08"

get_session_wifi
----------------

Get a JSON of the wifi devices (clients and access points) in the current session

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_wifi

.. confval:: mac

   Optional parameter to return the info of a specific endpoint

   :type: str

.. code-block:: yaml

   ###
   commands:
     - type: bettercap
       cmd: get_session_wifi
       mac: "32:26:9f:a4:08"
