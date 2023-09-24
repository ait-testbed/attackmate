.. _prep_sliver:

==============
Prepare Sliver
==============

`Sliver <https://github.com/BishopFox/sliver>`_ is a Post-Exploitation framework with implants for Linux, Windows and MacOs.
In order to use the sliver-commands in AttackMate, a sliver installation is required.
Sliver offers an API on port ``31337`` which is used by AttackMate to interact with it.
Follow the `Instructions offered by BishopFox <https://github.com/BishopFox/sliver>`_
to install the Sliver Framework. The simplest method is a curl oneliner:

::

  $ curl https://sliver.sh/install|sudo bash

Sliver will create an operator named "root" and save the configs under ``/root/.sliver-client/configs``
which can be used by AttackMate.
