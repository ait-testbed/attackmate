===========
http-client
===========

Execute HTTP-requests like curl does. This command also supports HTTP/2

.. code-block:: yaml

   ###
   commands:
     - type: http-client
       url: https://www.google.com
       http2: True

     - type: http-client
       cmd: POST
       url: https://api.myapp.tld
       useragent: "Mozilla Firefox 1/337"
       headers:
         "X-AUTH-TOKEN": "sometoken"
       cookies:
         mycookie: "cookie-value"
       data:
         view: edit
         id: 10

     - type: http-client
       cmd: PUT
       url: https://api.myapp.tld/dav
       local_path: /tmp/webshell.php



.. confval:: cmd

   The HTTP-Method to use. Supported methods are:

   * GET
   * POST
   * PUT
   * DELETE
   * PATCH
   * HEAD
   * OPTIONS

   :type: str
   :default: ``GET``

.. confval:: url

   Address of the target website.

   :type: str
   :required: ``True``

.. confval:: output_headers

   Store headers in the output.

   :type: str
   :default: ``False``

.. confval:: headers

   Include these extra headers in the request when sending HTTP to a server.

   :type: dict[str,str]

.. confval:: cookies

   Pass the data to the HTTP server in the Cookie header.

   :type: dict[str,str]

.. confval:: data

   Sends  the specified data in a POST request to the HTTP server, in the same
   way that a browser does when a user has filled in an HTML form and presses
   the submit button.

   :type: dict[str,str]

.. confval:: local_path

   Load content from the given file and send it via HTTP. This is useful for
   dav uploads.

   :type: str

.. confval:: useragent

   Change the user-agent string.

   :type: str
   :default: ``AttackMate``

.. confval:: follow

   Automatically follow redirects

   :type: bool
   :default: ``False``

.. confval:: verify

   This option makes attackmate skip the secure connection verification step and proceed without checking.

   :type: bool
   :default: ``False``

.. confval:: http2

   Try to use HTTP version 2. AttackMate will negotiate the HTTP version with the server and use HTTP2 if possible.

   :type: bool
   :default: ``False``
