.. _manual:

=========================
Installation from sources
=========================

AttackMate is written in python language. It can execute various pentesting and hacking tools.
Therefore, it is recommended to install AttackMate under Kali Linux. However, it should also
work on other Linux distributions. In order to prepare your system for AttackMate install the
following tools:

::

  $ sudo apt install python3 python3-pip git python3-venv libmagic1

.. note::

   python3-venv must only be installed if AttackMate should be installed in a virtual environment

Download the sources:

::

  $ git clone https://github.com/ait-aecid/attackmate.git
  $ cd attackmate

Optional: Create virtual environment and activate it:

::

  $ python3 -mvenv venv
  $ source venv/bin/activate

Finally install attackmate and it's dependencies:

::

  $ pip3 install .

.. warning::

   Please note that you need to :ref:`sliver-fix` if you want
   to use the sliver commands!
