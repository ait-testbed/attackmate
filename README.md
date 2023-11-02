# AttackMate

AttackMate is an attack orchestration tool that executes full attack-chains based on playbooks.

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

*Please note that AttackMate could easily executed in a dangerous way. For example by
parsing the RESULT_STDOUT of a malicious server. The server response could lead to
a command injection. Keep that in mind!

## License

[GPL-3.0](LICENSE)
