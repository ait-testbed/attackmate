=======
webserv
=======

Start a http-server and share a file. This command
will return after the first HTTP-request. To keep serving the file instead set keep_serving to True.
The webserv command has to be run in background mode, otherwise the playbook execution will halt until a request is received.
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

.. confval:: keep_servng

   Keep serving even after a request has been processed

   :type: bool
   :default: False
