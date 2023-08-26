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


The configuration-file is in yaml-format:

.. code-block:: yaml

   ###
   cmd_config:
     loop_sleep: 5

   msf_config:
     password: hackhelfer
     server: 10.18.3.86

   sliver_config:
     config_file: /home/attacker/.sliver-client/configs/attacker_localhost.cfg
