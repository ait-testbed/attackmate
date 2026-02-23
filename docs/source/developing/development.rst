.. _development:

===========
Development
===========

This section describes how to setup a development environment and how to contribute to `attackmate`.

.. note::

    Read the :ref:`Contribution Guide <contribution>` to follow and understand the development workflow.
    


Setup a development environment
===============================

For development we recommend using `uv`_. You can install all optional dependencies:

.. _uv: https://docs.astral.sh/uv/

::

    uv sync --dev

*Please note that this step is not necessary. `uv run --dev` will automatically download all dependencies.*


Use prek to run code checks
===========================

Every code contributer must use `prek`_ to run basic checks at commit time.
`prek` is configured via the existing `.pre-commit-config.yaml`
and can be installed as part of the `dev` extras. To ensure pre-commit hooks run before each commit, run:

.. _prek: https://github.com/j178/prek

::

    uv run prek install

To run the checks manually, you can execute:

::

    uv run prek run -a

Add tests and run pytest
========================

In oder to run the tests run the following command:

::

    uv run --dev pytest
