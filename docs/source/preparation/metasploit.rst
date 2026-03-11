.. _prep_msf:

==================
Prepare Metasploit
==================

It is recommended to install Metasploit as described in the official
`Metasploit documentation <https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html>`_.
On Kali Linux, you can also install it from the repositories using apt:

::

  $ sudo apt update && sudo apt install metasploit-framework


AttackMate communicates with Metasploit via the RPC daemon (``msfrpcd``). Start it
(optionally with a password) before running AttackMate:

::

   $ msfrpcd -P securepassword

Once started, ``msfrpcd`` listens on all interfaces on port ``55553``. Configure the
connection in AttackMate via :ref:`msf_config`.
