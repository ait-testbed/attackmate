.. _sliver:

======
sliver
======

Control the Sliver C2 server via its API. All commands use ``type: sliver``.

.. note::

   **For developers:** The ``sliver`` and ``sliver-session`` command families use a legacy
   ``type`` + ``cmd`` discrimination pattern and should not be replicated. New commands
   must define a unique ``type`` literal and handle sub-behavior branching via ``cmd``
   in the executor. See :ref:`command` for details.

start_https_listener
--------------------

Start an HTTPS listener on the Sliver server.

.. code-block:: yaml

   commands:
     - type: sliver
       cmd: start_https_listener
       host: 0.0.0.0
       port: 443


.. confval:: host

   Network interface to bind the listener to.

   :type: str
   :default: ``0.0.0.0``

.. confval:: port

   TCP port to listen on.

   :type: int
   :default: ``443``

.. confval:: domain

   Limit responses to specific domain.

   :type: str
   :default: `` ``

.. confval:: website

   Website name to associate with this listener.

   :type: str
   :default: `` ``

.. confval:: acme

   Attempt to provision a let's encrypt certificate.

   :type: bool
   :default: ``False``

.. confval:: persistent

   Keep the listener running across Sliver server restarts.

   :type: bool
   :default: ``False``

.. confval:: enforce_otp

   Require OTP authentication for connecting implants.

   :type: bool
   :default: ``True``

.. confval:: randomize_jarm

   Enable randomized JARM fingerprints.

   :type: bool
   :default: ``True``

.. confval:: long_poll_timeout

   Server-side long poll timeout(in seconds).

   :type: int
   :default: ``1``

.. confval:: long_poll_jitter

   Server-side long poll jitter(in seconds)

   :type: int
   :default: ``2``

.. confval:: timeout

   Command timeout in seconds.

   :type: int
   :default: ``60``


generate_implant
----------------

Generates a new sliver binary and saves the implant to a given path or to /tmp/<name>.
The path to the implant is saved and can be retrieved from the :ref:`builtin variable <builtin-variables>` ``$LAST_SLIVER_IMPLANT``.

.. code-block:: yaml

   commands:
     - type: sliver
       cmd: generate_implant
       c2url: "https://myC2url.com"
       name: "linux_implant"
       target: linux/amd64
       filepath: /path/to/implant/my_implant


.. confval:: target

   Target operating system and architecture. Supported values:

   * darwin/amd64
   * darwin/arm64
   * linux/386
   * linux/amd64
   * windows/386
   * windows/amd64

   :type: str
   :default: ``linux/amd64``

.. confval:: c2url

   URL which is used by the implant to reach the C2 server.

   :type: str
   :required: True

.. confval:: format

   Output format for the implant binary. One of:

   * EXECUTABLE
   * SERVICE
   * SHARED_LIB
   * SHELLCODE

   :type: str
   :default: ``EXECUTABLE``

.. confval:: name

   Name of the implant.
   This name is the session identifier used by :ref:`sliver-session <sliver_session>` commands.

   :type: str
   :required: True

.. confval:: filepath

   The local filepath to save the implant to. If omitted, the implant is saved to ``/tmp``.
   The filename will be randomly genrated and have the format ^tmp[a-z0-9]{8}$.


   :type: str
   :default: ``/tmp/<name>``

.. confval:: IsBeacon

   Generate a beacon-mode implant instead of a session-mode implant.

   :type: bool
   :default: ``False``

.. confval:: RunAtLoad

   Run the implant entrypoint from DllMain/Constructor (shared library only).

   :type: bool
   :default: ``False``

.. confval:: Evasion

   Enable evasion features such as overwriting user space hooks.

   :type: bool
   :default: ``False``
