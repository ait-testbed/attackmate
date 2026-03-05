.. _Overview:

=============
Configuration
=============

The configuration file can be passed via the ``--config`` parameter. If this parameter
is not used, attackmate will search at the following locations for the config-file:

#. **.attackmate.yml**
#. **$HOME/.config/attackmate.yml**
#. **/etc/attackmate.yml**

The optional configuration-file is in yaml-format and is divided into five sections:

* **cmd_config**: defines settings for all commands
* **msf_config**: connection settings for the msfrpcd
* **bettercap_config**: connection settings for the bettercap rest-api
* **sliver_config**: connection settings for the sliver-api
* **remote_config**: connection settings for the remote attackmate server

The following configuration file is an example for a basic configuration with
sliver and metasploit:

.. code-block:: yaml

   ###
   cmd_config:
     loop_sleep: 5
     command_delay: 0

   bettercap_config:
     default:
       url: "http://localhost:8081"
       username: user
       password: password

   msf_config:
     password: securepassword
     server: 127.0.0.1

   sliver_config:
     config_file: /home/attacker/.sliver-client/configs/attacker_localhost.cfg

For detailed information about the config sections see:

.. toctree::
   :maxdepth: 4

   config_vars
   command_config
   bettercap_config
   msf_config
   sliver_config
   remote_config
