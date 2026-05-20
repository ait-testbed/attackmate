.. _bettercap:

=========
bettercap
=========

This command communicates with the Bettercap REST API. It supports all
endpoints of the official API. Please see `Bettercap Rest-Api Docs  <https://www.bettercap.org/modules/core/apirest/>`_
for additional information. All commands return a json-formatted string.

All ``bettercap`` commands support the ``connection`` field, which specifies which configured
host to target. Connection profiles are defined in ``attackmate.yml`` under
:ref:`bettercap_config`. If ``connection`` is omitted, the first profile in the configuration
is used as the default.

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
     # this is executed on localhost (default):
     - type: bettercap
       cmd: get_events

.. note::

   To configure the connection to the bettercap REST API see :ref:`bettercap_config`


post_api_session
----------------

Post a command to the interactive Bettercap session.

.. confval:: data

   Key-value pairs of POST data to send to the session endpoint.

   :type: Dict[str, str]

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: post_api_session
       data:
         cmd: "net.sniff on"

get_file
--------

Get a file from the Bettercap API server.

.. confval:: filename

   Full path of the file to retrieve from the API server.

   :type: str

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_file
       filename: "/etc/passwd"

delete_api_events
-----------------

Clear the events buffer.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: delete_api_events

get_events
----------

Get all events from the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_events

get_session_modules
-------------------

Get all modules active in the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_modules

get_session_env
---------------

Get the environment variables of the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_env

get_session_gateway
-------------------

Get gateway information for the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_gateway

get_session_interface
---------------------

Get network interface information for the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_interface

get_session_options
-------------------

Get the configured options for the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_options

get_session_packets
-------------------

Get packet statistics for the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_packets

get_session_started_at
----------------------

Get the timestamp of when the current session was started.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_started_at

get_session_hid
---------------

Get a JSON list of HID devices discovered in the current session.

.. confval:: mac

   Optional. Filter results to a specific device by MAC address.

   :type: str
   :required: False

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_hid

     # Filter by MAC address:
     - type: bettercap
       cmd: get_session_hid
       mac: "32:26:9f:a4:08"

get_session_ble
---------------

Get a JSON list of BLE devices discovered in the current session.


.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_ble

.. confval:: mac

   Optional. Return the info of a specific device by MAC address.

   :type: str
   :required: False

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_ble
       mac: "32:26:9f:a4:08"

get_session_lan
---------------

Get a JSON of the lan devices in the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_lan

.. confval:: mac

   Optional. Return the info of a specific device by MAC address.

   :type: str
   :required: False

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_lan
       mac: "32:26:9f:a4:08"

get_session_wifi
----------------

Get a JSON of the wifi devices (clients and access points) in the current session.

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_wifi

.. confval:: mac

   Optional. Return the info of a specific device by MAC address.

   :type: str
   :required: False

.. code-block:: yaml

   commands:
     - type: bettercap
       cmd: get_session_wifi
       mac: "32:26:9f:a4:08"
