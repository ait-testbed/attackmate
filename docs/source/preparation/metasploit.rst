==================
Prepare Metasploit
==================

It is recommended to install Metasploit as it is described in the
`Metasploit documentation <https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html>`_.
If you run Kali Linux, you could also install it from the Kali Linux repositories using apt:

::

  $ sudo apt update && apt install metasploit-framework


AttackMate needs the RPC-daemon(msfrpcd) for communication with Metasploit.
It is possible to protect the daemon with a password. The following example
starts the msfrpcd with a password:

::

  $ msfrpcd -P securepassword

After starting the msfrpcd it will listen on all interface at port ``55553``.
