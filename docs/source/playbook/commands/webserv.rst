=======
webserv
=======

Start a simple HTTP server to serve a single file. By default, the server stops after
handling the first request. Set :confval:`keep_serving` to ``True`` to continue serving.

.. warning::

   This command blocks until a request is received. Always run it in
   :confval:`background` mode to avoid halting playbook execution.

.. code-block:: yaml

   commands:
     - type: webserv
       local_path: "/tmp/webshell.php"
       port: 8000
       background: true

.. confval:: local_path

   Path to the file to serve.

   :type: str
   :required: True

.. confval:: port

   Port to listen on.

   :type: int
   :default: ``8000``
   :required: False

.. confval:: address

   Address to listen on.

   :type: str
   :default: ``0.0.0.0``
   :required: False

.. confval:: keep_serving

   Continue serving the file after the first request has been handled.

   :type: bool
   :default: ``False``
   :required: False
