===========
http-client
===========

Send HTTP requests with support for common methods, custom headers, cookies, and HTTP/2.

.. code-block:: yaml

   commands:
      # Simple HTTP/2 GET request:
     - type: http-client
       url: https://www.google.com
       http2: True

      # POST request with headers, cookies, and form data:
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

      # PUT request uploading a local file
     - type: http-client
       cmd: PUT
       url: https://api.myapp.tld/dav
       local_path: /tmp/webshell.php



.. confval:: cmd

   HTTP method to use. Supported values: ``GET``, ``POST``, ``PUT``, ``DELETE``,
   ``PATCH``, ``HEAD``, ``OPTIONS``.

   :type: str
   :default: ``GET``

.. confval:: url

   URL of the target.

   :type: str
   :required: True

.. confval:: output_headers

   Store headers in the output.

   :type: str
   :default: ``False``

.. confval:: headers

   Additional HTTP headers to include in the request.

   :type: dict[str,str]

.. confval:: cookies

   Cookies to send in the ``Cookie`` header.

   :type: dict[str,str]

.. confval:: data

   Form data to send in the request body. Equivalent to submitting an HTML form.
   Typically used with ``POST``.

   :type: dict[str,str]

.. confval:: local_path

   Path to a local file whose contents will be sent as the request body. Useful
   for WebDAV uploads.

   :type: str

.. confval:: useragent

   Override the ``User-Agent`` header.

   :type: str
   :default: ``AttackMate``

.. confval:: follow

   Automatically follow HTTP redirects.

   :type: bool
   :default: ``False``

.. confval:: verify

   Verify the server's TLS certificate. Set to ``False`` to skip verification
   (e.g. for self-signed certificates).

   :type: bool
   :default: ``False``

.. confval:: http2

   Negotiate HTTP/2 with the server and use it if supported.

   :type: bool
   :default: ``False``
