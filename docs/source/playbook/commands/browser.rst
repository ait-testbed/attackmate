=======
browser
=======

Execute commands using a Playwright-managed Chromium browser. This executor can launch a browser, navigate to pages, click elements, type into fields, and take screenshots.

.. note::

   By default, each command runs in an ephemeral browser session that is launched and
   destroyed automatically. To persist browser state (cookies, localStorage,
   etc.) across multiple commands, use the :confval:`creates_session` to open a named
   session and :confval:`session` to reuse it.

.. code-block:: yaml

   vars:
     $URL: "https://www.wikipedia.org/"

   commands:
     # Create a new named browser session called "my_session"
     - type: browser
       cmd: visit
       url: $URL
       creates_session: my_session

     # Type into a field, reusing the named session:
     - type: browser
       cmd: type
       selector: "input[id='searchInput']"
       text: "Test"
       session: "my_session"

     # Click on the "submit" button, reusing the named session:
     - type: browser
       cmd: click
       selector: "button[type='submit']"
       session: "my_session"

    # Take a screenshot of the current page, reusing the named session:
     - type: browser
       cmd: screenshot
       screenshot_path: "example.png"
       session: "my_session"

     # Open a page in an ephemeral session (automatically closed after command)
     - type: browser
       cmd: visit
       url: "https://www.google.com"

.. confval:: cmd

   Specifies the browser action to execute. One of ``visit``, ``click``, ``type``, ``screenshot``.

   :type: str
   :default: ``visit``

.. confval:: url

   URL to navigate to for the ``visit`` command.

   :type: str
   :required: when ``cmd: visit``

.. confval:: selector

   CSS selector identifying the target element to interact with for the ``click`` or ``type`` commands.

   :type: str
   :required: when ``cmd: click`` OR ``cmd: type``

.. confval:: text

   Text to type into the specified element for the ``type`` command.

   :type: str
   :required: when ``cmd: type``

.. confval:: screenshot_path

   Filepath where a screenshot should be saved for the ``screenshot`` command.

   :type: str
   :required: when ``cmd: screenshot``

.. confval:: creates_session

   Name of a new browser session to create. Once created, the session is retained in the
   session store for reuse by subsequent ``browser`` commands that specify ``session``.

   If a session with the same name already exists, it is automatically closed and replaced.

   :type: str
   :required: False

.. confval:: session

   Name of an existing session to reuse. This session must have been created previously with
   ``creates_session``. If omitted, the command will either create a new ephemeral session
   (destroyed after the command finishes) or reuse the default ephemeral session if the code
   supports that usage pattern.

   :type: str

   :required: False

.. confval:: headless

   Run the browser in headless mode.
   Useful for CI/CD pipelines or servers without a GUI.

   :type: bool

   :required: False

   :default: ``False``

   Example:

   .. code-block:: yaml

      - type: browser
        cmd: visit
        url: "https://example.com"
        creates_session: ci_session
        headless: true
