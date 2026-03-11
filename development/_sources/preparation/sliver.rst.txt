.. _prep_sliver:

==============
Prepare Sliver
==============

`Sliver <https://github.com/BishopFox/sliver>`_ is a post-exploitation framework with
implants for Linux, Windows, and macOS. AttackMate communicates with Sliver via its API
on port ``31337``.

Installation
------------

Follow the `installation instructions by BishopFox <https://github.com/BishopFox/sliver>`_
to set up the Sliver framework. The quickest method is:

::

  $ curl https://sliver.sh/install | sudo bash

After installation, Sliver creates an operator named ``root`` and stores its configuration
under ``/root/.sliver-client/configs``, which AttackMate uses to connect.

Configuration
-------------

AttackMate requires Sliver to run in daemon mode. Ensure the following is set in
``.sliver/configs/server.json``:

::

  "daemon-mode": "true"
