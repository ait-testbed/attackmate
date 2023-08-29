.. _sliver:

======
sliver
======

There are multiple commands from type 'sliver' to controll the sliver-server via API.

start_https_listener
--------------------

Start an HTTPS-Listener

.. code-block:: yaml

   ###
   commands:
     - type: sliver
       cmd: start_https_listener
       host: 0.0.0.0
       port: 443


.. confval:: host

   Interface to bind server to.

   :type: str
   :default: ``0.0.0.0``

.. confval:: port

   TCP-Listen port

   :type: int
   :default: ``443``

.. confval:: domain

   Limit responses to specific domain

   :type: str
   :default: `` ``

.. confval:: website

   Website name

   :type: str
   :default: `` ``

.. confval:: acme

   Attempt to provision a let's encrypt certificate

   :type: bool
   :default: ``False``

.. confval:: persistent

   Make persistent across restarts.

   :type: bool
   :default: ``False``

.. confval:: enforce_otp

   Enable or disable OTP authentication

   :type: bool
   :default: ``True``

.. confval:: randomize_jarm

   Enable randomized Jarm fingerprints

   :type: bool
   :default: ``True``

.. confval:: long_poll_timeout

   Server-Side long poll timeout(in seconds)

   :type: int
   :default: ``1``

.. confval:: long_poll_jitter

   Server-Side long poll jitter(in seconds)

   :type: int
   :default: ``2``

.. confval:: timeout

   Command timeout in seconds.

   :type: int
   :default: ``60``


generate_implant
----------------

Generate a new sliver binary and saves the implant to a given path or to /tmp/<name>.

.. code-block:: yaml

   ###
   commands:
     - type: sliver
       cmd: start_https_listener
       host: 0.0.0.0
       port: 443

     - type: sliver
       cmd: generate_implant
       name: "linux_implant"
       target: linux/amd64


.. confval:: target

   Compile the binary for the given operatingsystem to the given architecture. The
   following targets are supported:

   * darwin/amd64
   * darwin/arm64
   * linux/386
   * linux/amd64
   * windows/386
   * windows/amd64

   :type: str
   :default: ``linux/amd64``

.. confval:: c2url

   Url which is used by the implant to find the C2 server.

   :type: str
   :required: True

.. confval:: format

   Specifies the output format for the implant. Valid formats are:

   * EXECUTABLE
   * SERVICE
   * SHARED_LIB
   * SHELLCODE

   :type: str
   :default: ``EXECUTABLE``

.. confval:: name

   Name of the Implant

   :type: str
   :required: True

.. confval:: filepath

   The local filepath to save the implant to.

   :type: str
   :default: ``/tmp/<name>``

.. confval:: IsBeacon

   Generate a beacon binary

   :type: bool
   :default: False

.. confval:: RunAtLoad

   Run the implant entrypoint from DllMain/Constructor(shared library only)

   :type: bool
   :default: ``False``

.. confval:: Evasion

   Enable evasion features (e.g. overwrite user space hooks)

   :type: bool
   :default: ``False``

   :type: bool
   :default: False
