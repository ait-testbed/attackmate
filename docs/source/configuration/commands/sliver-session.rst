.. _sliver_session:

==============
sliver-session
==============

There are multiple commands from type 'sliver-session' to execute commands in an
active sliver session.

ls
--

List files and directories on the remote host

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: ls
       remote_path: /etc


.. confval:: remote_path

   Path to list all files

   :type: str
   :required: ``True``


cd
--

Change the working directory

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: cd
       remote_path: /home


.. confval:: remote_path

   Path to change to

   :type: str
   :required: ``True``


netstat
-------

Print network connection information

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: netstat
       tcp: True
       udp: True
       ipv4: True
       ipv6: False
       listening: True


.. confval:: tcp

   Display information about TCP sockets

   :type: bool
   :default: ``True``

.. confval:: udp

   Display information about UDP sockets

   :type: bool
   :default: ``True``

.. confval:: ipv4

   Display information about IPv4 sockets

   :type: bool
   :default: ``True``

.. confval:: ipv6

   Display information about IPv6 sockets

   :type: bool
   :default: ``True``

.. confval:: listening

   Display information about listening sockets

   :type: bool
   :default: ``True``


execute
-------

Execute a program on the remote system

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: execute
       exe: /usr/bin/grep
       args:
         - root
         - /etc/passwd
       output: True


.. confval:: exe

   Command to execute

   :type: str
   :required: ``True``

.. confval:: args

   List of command arguments

   :type: List[str]

.. confval:: output

   Capture command output

   :type: bool
   :default: ``True``


mkdir
-----

Create a remote directory.

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: mkdir
       remote_path: /tmp/somedirectory


.. confval:: remote_path

   Path to the directory to create

   :type: str
   :required: ``True``


ifconfig
--------

View network interface configurations

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: ifconfig

ps
--

List processes of the remote system

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: ps


pwd
---

Print working directory of the active session.

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: pwd

download
--------

Download a file or directory from the remote system. Directories will be downloaded as a gzipped tar-file.

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: download
       remote_path: /root
       recurse: True


.. confval:: remote_path

   Path to the file or directory to download

   :type: str
   :required: ``True``

.. confval:: local_path

   Local path where the downloaded file will be saved.

   :type: str
   :required: ``False``
   :default: ``.``

.. confval:: recurse

   Recursively downloaded all files in a directory.

   :type: bool
   :default: ``False``

upload
------

Upload a file to the remote system.

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: upload
       remote_path: /tmp/somefile
       local_path: /home/user/somefile

.. confval:: remote_path

   Path to the file or directory to upload to

   :type: str
   :required: ``True``

.. confval:: local_path

   Local path to the file to upload

   :type: str

.. confval:: is_ioc

   Track uploaded file as an ioc

   :type: bool
   :default: ``False``


process_dump
------------

Dumps the process memory of a given pid to a local file.

.. code-block:: yaml

   ###
   commands:
     - type: sliver-session
       cmd: process_dump
       pid: 102
       local_path: /home/user/some_service.dump

.. confval:: pid

   Target Pid

   :type: int
   :required: ``True``


.. confval:: local_path

   Save to file.

   :type: str
   :required: ``True``


rm
--

Delete a remote file or directory.

.. confval:: remote_path

   Path to the file to remove

   :type: str
   :required: ``True``

.. confval:: recursive

   Recursively remove files

   :type: bool
   :default: ``False``

.. confval:: force

   Ignore safety and forcefully remove files

   :type: bool
   :default: ``False``


terminate
---------

Kills a remote process designated by PID

.. confval:: pid

   PID of the process to kill.

   :type: int
   :required: ``True``

.. confval:: force

   Disregard safety and kill the PID.

   :type: bool
   :default: ``False``
