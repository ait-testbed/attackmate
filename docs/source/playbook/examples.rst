========
Examples
========

The following example playbooks require an installed `Metasploitable2 <https://docs.rapid7.com/metasploit/metasploitable-2/>`_ virtual machine and
a `Kali Linux <https://www.kali.org/>`_ with some packages installed:

* AttackMate
* NMap
* THC Hydra
* Metasploit
* nikto
* curl

.. note::

   It is advised to copy the example playbooks to the directory "./playbooks"

Prepare Kali-Linux:

::

  $ sudo apt install nikto nmap curl seclists hydra
  $ cp -r examples playbooks

Playbooks
---------

* `HTTP-client example <https://github.com/ait-aecid/attackmate/blob/main/examples/http-put_example.yml>`_
* `Include command example <https://github.com/ait-aecid/attackmate/blob/main/examples/include.yml>`_
* `Only If example <https://github.com/ait-aecid/attackmate/blob/main/examples/only_if.yml>`_
* `SSH/SFTP example <https://github.com/ait-aecid/attackmate/blob/main/examples/ssh_example.yml>`_
* `Upgrade meterpreter shell <https://github.com/ait-aecid/attackmate/blob/main/examples/upgrade_to_meterpreter.yml>`_
* `Fileshare via webserv example <https://github.com/ait-aecid/attackmate/blob/main/examples/webserv.yml>`_
* `Command injection and MSF multi handler example <https://github.com/ait-aecid/attackmate/blob/main/examples/webdemo.yml>`_
