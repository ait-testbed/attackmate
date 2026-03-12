.. _vnc:

===
vnc
===

Execute commands on a remote host via VNC, using the
`vncdotool <https://github.com/sibson/vncdotool>`_ library. Connection settings are
cached after the first command, so subsequent commands only need to specify what changes.

.. warning::

   VNC sessions must be explicitly closed with ``cmd: close``, otherwise AttackMate
   will hang on exit.

.. note::

   Background mode is not supported for this commands.

.. code-block:: yaml

   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $PORT: 5900
     $DISPLAY: 1
     $PASSWORD: password

   commands:
     # Open a connection, take a screenshot, and create a named session:
     - type: vnc
       cmd: capture
       filename: screenshot.png
       hostname: $SERVER_ADDRESS
       port: $PORT
       display: $DISPLAY
       password: $PASSWORD
       creates_session: my_session

     # Type text using the existing session:
     - type: vnc
       cmd: type
       input: "echo hello world"
       session: my_session

     # Close the session and remove it from the session store:
     - type: vnc
       cmd: close
       session: my_session

.. confval:: cmd

   The VNC action to perform. One of:

   * ``capture`` — take a screenshot and save it to :confval:`filename`
   * ``expectscreen`` — compare the current screen against :confval:`filename`; continue only if they match within :confval:`maxrms`
   * ``type`` — type a string on the remote host via :confval:`input`
   * ``key`` — press a key on the remote host via :confval:`key`
   * ``click`` — left-click at the current cursor position
   * ``rightclick`` — right-click at the current cursor position
   * ``move`` — move the cursor to (:confval:`x`, :confval:`y`)
   * ``close`` — close the session and remove it from the session store

   :type: str
   :required: True

Connection
----------

.. confval:: hostname

   Hostname or IP address of the remote VNC server.

   :type: str

.. confval:: port

   Port to connect to on the remote host.

   :type: int
   :default: ``5900``
   :required: False

.. confval:: display

   Display number to connect to on the remote host.

   :type: int
   :default: ``1``
   :required: False

.. confval:: password

   Password for VNC authentication.

   :type: str

.. confval:: connection_timeout

   Timeout in seconds for the initial connection to be established.
   Must be set in the first command that opens the connection.

   :type: int
   :default: ``10``
   :required: False

.. confval:: expect_timeout

   Timeout in seconds for a command to complete. Passed to the VNC client when
   the connection is first established — must be set in the first command that
   opens the connection.

   :type: int
   :default: ``60``
   :required: False

Sessions
--------

.. confval:: creates_session

   Name to assign to the session opened by this command. Can be reused in subsequent
   commands via :confval:`session`. If omitted and no prior session exists, a session
   named ``default`` is created automatically.

   :type: str
   :required: False

.. confval:: session

   Name of an existing VNC session to reuse. The session must have been created
   previously via :confval:`creates_session`.

   :type: str
   :required: False

Actions
-------

.. confval:: filename

   Path to save a screenshot (``capture``) or path to an image file to compare
   against the current screen (``expectscreen``).

   :type: str
   :required: when ``cmd: capture`` or ``cmd: expectscreen``

.. confval:: maxrms

   Maximum RMS (root mean square) error allowed when comparing screens with
   ``expectscreen``. Lower values require a closer match.

   :type: float
   :default: ``0``
   :required: False

.. confval:: input

   Text to type on the remote host. Used with the ``type`` command.

   :type: str
   :required: when ``cmd: type``

.. confval:: key

   Key to press on the remote host. Used with the ``key`` command.

   :type: str
   :required: when ``cmd: key``

.. confval:: x

   Horizontal cursor position for the ``move`` command.

   :type: int
   :required: when ``cmd: move``

.. confval:: y

   Vertical cursor position for the ``move`` command.

   :type: int
   :required: when ``cmd: move``
