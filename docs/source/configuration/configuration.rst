.. _Overview:

========
Overview
========

AttackMate ships with a executable stub called "attackmate" that can be called like follows:

.. code-block::

   attackmate -h
   usage: attackmate [-h] --config CONFIG [--debug] [--version]

   AttackMate is an attack orchestration tool that executes full attack-chains based on playbooks.

   options:
     -h, --help       show this help message and exit
     --config CONFIG  Attack-Playbook in yaml-format
     --debug          Enable verbose output
     --version        show program's version number and exit

   (Austrian Institute of Technology) https://aecid.ait.ac.at Version: 0.2.0


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
