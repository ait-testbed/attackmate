.. _uv:

=========================
Installation with uv
=========================

It is possible install AttackMate using `uv <https://docs.astral.sh/uv/>`_ package manager.


Installation Steps
==================

1. Install uv:

::

  $ curl -LsSf https://astral.sh/uv/install.sh | sh

2. Git clone AttackMate

::

  $ git clone https://github.com/ait-testbed/attackmate.git

3. Navigate into the repository

::

  $ cd attackmate


4. Create a virtual environment with uv

::

  $ uv venv

4. Create a package using uv

::

     $ uv build

5. Install AttackMate using

::

     $ uv pip install



