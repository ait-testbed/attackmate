===
vnc
===

Execute commands on a remote server via VNC. Uses the `vncdotool <https://github.com/sibson/vncdotool>` library.

.. note::

   This command caches all the settings so
   that they only need to be defined once.

.. code-block:: yaml

   vars:
     $SERVER_ADDRESS: 192.42.0.254
     $PORT: 5900
     $DISPLAY: 1
     $PASSWORD: password

   commands:
     # creates new vnc-connection and session. If creates_session is omitted, a session named "default" is created
     - type: vnc
       cmd: capture
       filename: screenshot.png
       hostname: $SERVER_ADDRESS
       port: $PORT
       display: $DISPLAY
       password: $PASSWORD
       creates_session: my_session

     # reuses existing session "my_session
     - type: vnc
       cmd: type
       input: "echo hello world"
       session: my_session

     # closes existing session "my_session" and deletes from session store
     - type: vnc
       cmd: close
       session: my_session


.. confval:: cmd

   One of ``type``, ``key``, ``capture``, ``move``, ``expectscreen``, ``close``

   :type: str

.. confval:: hostname

   This option sets the hostname or ip-address of the
   remote ssh-server.

   :type: str

.. confval:: port

   Port to connect to on the remote host.

   :type: int
   :default: ``5900``

.. confval:: display

   Specifies the display to use on the remote machine.

   :type: str

.. confval:: password

   Specifies the password to use

   :type: str

.. confval:: filename

   Path where a screeshot ``capture`` should be saved, or file to compare a screenshot with ``expext screen``.

   :type: str

.. confval:: maxrms

   Metric to compare a screenshot with ``expext screen``.

   :type: int

.. confval:: input

   text to type with the command ``type``

   :type: str

.. confval:: key

   key to press with the command ``key``

   :type: str


.. confval:: x

   x position ot move the cursor to with the command ``move``

   :type: int

.. confval:: y

   y position ot move the cursor to ``move``

   :type: int


.. confval:: creates_session

   A session name that identifies the session that is created when
   executing this command. This session name can be used by using the
   option ``session`` in another vnc-command.
   If no ``creates_session`` name is defined and no previous session is used a session named ``default`` is created.

   :type: str

.. confval:: session

   Reuse an existing session. This setting works only if another
   vnc-command was executed with the command-option "creates_session"

   :type: str






