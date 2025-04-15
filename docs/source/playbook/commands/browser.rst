=======
browser
=======

Execute commands using a Playwright-managed browser (Chromium). This executor can launch a browser, navigate to pages, click elements, type into fields, and take screenshots.

.. note::

   By default, if no session is provided or created, the command will run in an ephemeral browser session
   (launched and destroyed for each command). If you want to persist browser state (cookies, localStorage,
   etc.) across multiple commands, use the :confval:`creates_session` or :confval:`session` options.

.. code-block:: yaml

   vars:
     $URL: "https://www.wikipedia.org/"

   commands:
     # Create a new named browser session called "my_session"
     - type: browser
       cmd: visit
       url: $URL
       creates_session: my_session

     # Reuse the existing "my_session" to type text into an input field
     - type: browser
       cmd: type
       selector: "input[id='searchInput']"
       text: "Test"
       session: "my_session"

     # Click on the "submit" button, still reusing "my_session"
     - type: browser
       cmd: click
       selector: "button[type='submit']"
       session: "my_session"

    # Take a screenshot of the current page in the "my_session"
     - type: browser
       cmd: screenshot
       screenshot_path: "example.png"
       session: "my_session"

     # Open a page in an ephemeral session (automatically closed)
     - type: browser
       cmd: visit
       url: "https://www.google.com"

.. confval:: cmd

   Specifies the browser action to execute. One of ``visit``, ``click``, ``type``, ``screenshot``.

   :type: str

.. confval:: url

   URL to visit for the ``visit`` command.

   :type: str

.. confval:: selector

   CSS selector identifying the element to interact with for the ``click`` or ``type`` commands.

   :type: str

.. confval:: text

   Text to type into the specified element for the ``type`` command.

   :type: str

.. confval:: screenshot_path

   Specifies the file path where a screenshot should be saved for the ``screenshot`` command.

   :type: str

.. confval:: creates_session

   A session name to create when running this command. Once created, the session is retained in the
   session store for reuse by subsequent ``browser`` commands that specify ``session``.

   If a session of the same name already exists, it is automatically closed before creating the new one.

   :type: str

.. confval:: session

   Name of an existing session to reuse. This session must have been created previously with
   ``creates_session``. If omitted, the command will either create a new ephemeral session
   (destroyed after the command finishes) or reuse the default ephemeral session if the code
   supports that usage pattern.

   :type: str
