AttackMate <img alt="Logo" src="/images/AttackMate_logo.svg" align="right" height="90">
==========
[![Build Status](https://aecidjenkins.ait.ac.at/buildStatus/icon?job=AECID%2FAECID%2Fattackmate%2Fmain)]( "https://aecidjenkins.ait.ac.at/job/AECID/job/AECID/job/attackmate/job/main/")

AttackMate is a tool to automate cyber attack scenarios that supports scripting of attack techniques across all phases of the Cyber Kill Chain. AttackMate's design principles aim to integrate with penetration testing and attack emulation frameworks such as Metasploit and Sliver Framework and enables simple execution of commands via shell or ssh. For example, AttackMate enables to execute Metasploit modules or generate payloads and run commands in Metasploit sessions. Moreover, it is able to generate Sliver implants, automatize Sliver to send C2 commands, and configure and compile LD_PRELOAD-rootkits. AttackMate also offers a simple interface to automate shell or ssh interaction, run commands in background mode, transfer files via sftp, and start http clients or servers. All attack steps may be scheduled, chained, and repeatedly executed using a simple configuration file that supports variable declarations and conditional workflows.


![AttackMate Schema](docs/source/images/attackmate-schema.png "AttackMate Schema")


## Requirements

* python >= 3.10
* libmagic

## Installation

Manually:

```
$ git clone https://github.com/ait-aecid/attackmate.git
$ cd attackmate
$ pip3 install .
```

Using pip:

```
$ pip3 install attackmate
```

## Execute

```
$ attackmate playbook.yml
```

![AttackMate Demo](docs/source/images/Demo.gif "AttackMate Demo")

## Documentation

Please take a look at our documentation for how to install and use attackmate:

* [Installation](https://aeciddocs.ait.ac.at/attackmate/current/installation/index.html)
* [Documentation](https://aeciddocs.ait.ac.at/attackmate/current)
* [Command Reference](https://aeciddocs.ait.ac.at/attackmate/current/playbook/commands/index.html)
* [Example Playbooks](https://aeciddocs.ait.ac.at/attackmate/current/playbook/examples.html)

## Disclaimer

AttackMate is purely for educational and academic purposes. The software is provided "as is"
and the authors are not responsible for any damage or mishaps that may occur during its use.

Do not attempt to use AttackMate to violate the law. Misuse of the provided software and
information may result in criminal charges.

## Security

AttackMate should only be executed against own test or training systems.
For this reason, every software bug is treated equally, regardless of
whether it is security relevant or not.

*Please note that AttackMate could easily be executed in a dangerous way. For example, by
parsing the RESULT_STDOUT of a malicious server. The server response could lead to
a command injection. Keep that in mind!

## License

[GPL-3.0](LICENSE)
