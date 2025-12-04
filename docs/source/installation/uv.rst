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

5. Install AttackMate and it`s dependencies using

::

     $ uv pip install .


6. You can run AttackMate in the project environment with

::

     $ uv run attackmate



.. warning::

   Please note that you need to :ref:`sliver-fix` if you want
   to use the sliver commands!
