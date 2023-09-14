=======
webserv
=======

Start a http-server and share a file. This command
will return after the first HTTP-request.

.. code-block:: yaml

   ###
   commands:
     - type: webserv
       local_path: "/tmp/webshell.php"
       port: 8000


.. confval:: local_path

   Path to the file to share

   :type: str
   :required: ``True``


.. confval:: port

   Port to listen

   :type: int
   :default: ``8000``

.. confval:: address

   Address to listen

   :type: str
   :default: ``0.0.0.0``
