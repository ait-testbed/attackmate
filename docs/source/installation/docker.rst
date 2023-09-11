========================
Installation with Docker
========================

AttackMate can be run inside Docker containers. In order to build
the image, download the sources first:

::

  $ git clone https://github.com/ait-aecid/attackmate.git
  $ cd attackmate


Build the image using the following command:

::

  $ docker build -t attackmate -f Dockerfile .

.. note::

   Docker will also compile grpcio from sources in order to make
   the sliver-api work. This might take a while.
