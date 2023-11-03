.. _sliver-fix:

==================
Install sliver-fix
==================

Currently there is a `nasty bug with grpcclient and TLS1.3 <https://github.com/moloch--/sliver-py/issues/28`_
that breaks the communication between Sliver-API and AttackMate. In order to make
AttackMate work with the Sliver-API it is necessary to manually compile grpc with
the environment variable ``GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=True``


.. note::

   Please note that this fix is already included in the Dockerfile.

First install all required build-tools. This example will install the build-tools
in Debian-based distributions:

::

  $ sudo apt-get install -y git build-essential python3-dev libssl-dev

If you are inside the attackmate repository, change to another directory:

::

  $ cd ..

Next download the grpc-sources, update the submodules and install the
dependencies:

::

  (venv)$ git clone https://github.com/grpc/grpc && cd grpc
  (venv)$ git submodule update --init
  (venv)$ pip install -r requirements.txt

Now remove the packages we want to compile by our own:

::

  (venv)$ pip uninstall --yes protobuf
  (venv)$ pip uninstall --yes grpcio-tools

Install the proper versions:

::

  (venv)$ pip install --no-input protobuf==3.20.*
  (venv)$ pip install --no-input grpcio-tools

And compile grpc:

::

  (venv)$ GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=True pip install --use-pep517 --no-input .
