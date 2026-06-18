.. _sliver_session:

==============
sliver-session
==============

Execute commands within an active Sliver implant session. All commands require a
:confval:`session` field identifying the target implant.

.. note::

   **For developers:** The ``sliver`` and ``sliver-session`` command families use a legacy
   ``type`` + ``cmd`` discrimination pattern and should not be replicated. New commands
   must define a unique ``type`` literal and handle sub-behavior branching via ``cmd``
   in the executor. See :ref:`command` for details.

.. confval:: session

   Name of the Sliver implant session to operate in. The implant must have been
   generated and deployed previously via the sliver :ref:`generate_implant <sliver>` command.

   :type: str
   :required: True

File System
-----------

ls
^^^

List files and directories on the remote host.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: ls
       remote_path: /etc
       session: implant-name


.. confval:: remote_path

   Path to list all files.

   :type: str
   :required: True


cd
^^^

Change the working directory of the active session.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: cd
       remote_path: /home
       session: implant-name


.. confval:: remote_path

   Path to change to

   :type: str
   :required: True



mkdir
^^^^^

Create a remote directory.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: mkdir
       remote_path: /tmp/somedirectory
       session: implant-name


.. confval:: remote_path

   Path to the directory to create.

   :type: str
   :required: True


pwd
^^^

Print working directory of the active session.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: pwd
       session: implant-name


rm
^^^

Delete a remote file or directory.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: rm
       remote_path: /tmp/somefile
       session: implant-name

.. confval:: remote_path

   Path to the file to remove.

   :type: str
   :required: True

.. confval:: recursive

   Recursively remove files

   :type: bool
   :default: ``False``

.. confval:: force

   Ignore safety and forcefully remove files.

   :type: bool
   :default: ``False``

download
^^^^^^^^

Download a file or directory from the remote system. Directories will be downloaded as a gzipped tar-file.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: download
       remote_path: /root
       recurse: True
       session: implant-name


.. confval:: remote_path

   Path to the file or directory to download.

   :type: str
   :required: True

.. confval:: local_path

   Local path where the downloaded file will be saved.

   :type: str
   :required: False
   :default: ``.``

.. confval:: recurse

   Recursively downloaded all files in a directory.

   :type: bool
   :default: ``False``

upload
^^^^^^

Upload a file to the remote system.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: upload
       remote_path: /tmp/somefile
       local_path: /home/user/somefile
       session: implant-name

.. confval:: remote_path

   Destination path on the remote host.

   :type: str
   :required: True

.. confval:: local_path

   Path to the local file to upload.

   :type: str

.. confval:: is_ioc

   Mark the uploaded file as an indicator of compromise (IOC) for tracking purposes.

   :type: bool
   :default: ``False``

Network
-------

netstat
^^^^^^^

Display network connection information for the remote host.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: netstat
       tcp: True
       udp: True
       ipv4: True
       ipv6: False
       listening: True
       session: implant-name


.. confval:: tcp

   Display information about TCP sockets.

   :type: bool
   :default: ``True``

.. confval:: udp

   Display information about UDP sockets.

   :type: bool
   :default: ``True``

.. confval:: ipv4

   Display information about IPv4 sockets.

   :type: bool
   :default: ``True``

.. confval:: ipv6

   Display information about IPv6 sockets.

   :type: bool
   :default: ``True``

.. confval:: listening

   Display information about listening sockets

   :type: bool
   :default: ``True``

ifconfig
^^^^^^^^

Display network interface configuration of the remote host.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: ifconfig
       session: implant-name


Processes
---------

ps
^^^

List processes of the remote system.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: ps
       session: implant-name

execute
^^^^^^^

Execute a program on the remote host.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: execute
       exe: /usr/bin/grep
       args:
         - root
         - /etc/passwd
       output: True
       session: implant-name


.. confval:: exe

   Command to execute.

   :type: str
   :required: True

.. confval:: args

   List of command arguments.

   :type: List[str]

.. confval:: output

   Capture command output.

   :type: bool
   :default: ``True``

terminate
^^^^^^^^^

Kill a process on the remote host by PID.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: terminate
       pid: 1234
       session: implant-name

.. confval:: pid

   PID of the process to kill.

   :type: int
   :required: True

.. confval:: force

   Disregard safety and kill the process.

   :type: bool
   :default: ``False``

Memory
------

process_dump
^^^^^^^^^^^^

Dump the memory of a running process to a local file.

.. code-block:: yaml

   commands:
     - type: sliver-session
       cmd: process_dump
       pid: 102
       local_path: /home/user/some_service.dump
       session: implant-name

.. confval:: pid

   Target PID.

   :type: int
   :required: True


.. confval:: local_path

   Save to file.

   :type: str
   :required: True
