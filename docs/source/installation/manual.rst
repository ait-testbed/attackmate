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

   ``python3-venv`` only needs to be installed if AttackMate should be installed in a virtual environment.

Download the sources:

::

  $ git clone https://github.com/ait-aecid/attackmate.git
  $ cd attackmate

**Option A: Install with pip**

Optional: Create a virtual environment and activate it:

::

  $ python3 -mvenv venv
  $ source venv/bin/activate

Install AttackMate and its dependencies:

::

  $ pip3 install .

**Option B: Install with uv**

``uv`` manages the virtual environment and dependencies automatically — no manual venv setup needed:

::

  $ pip3 install uv
  $ uv sync

Run AttackMate via:

::

  $ uv run attackmate playbook.yml

.. warning::

   Please note that you if you install from source you also need to install :ref:`sliver-fix` if you want
   to use the sliver commands!
   The Dockerfile and ansible role :ref:`ansible` already include the sliver-fix.
