# AttackMate

AttackMate is an attack orchestration tool that executes full attack-chains based on playbooks.

![AttackMate Schema](images/attackmate-schema.png "AttackMate Schema")

## Requirements

AttackMate can use Metasploit-Module. For this feature it is
required to start the Metasploit-RPC-Daemon:

```
msfrpcd -P securepassword
```

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

## Documentation

Please take a look at our documentation for how to install and use attackmate:

* [Installation](https://aeciddocs.ait.ac.at/attackmate/current/readme_link.html#)
* [Configuration](https://aeciddocs.ait.ac.at/attackmate/current/configuration/configuration.html)
* [Documentation](https://aeciddocs.ait.ac.at/attackmate)

## Disclaimer

AttackMate is for research and training purposes only. Please respect our philosophy and
do not damage any computer systems.

## Security

AttackMate should only be executed against own test or training systems.
For this reason, every software bug is treated equally, regardless of
whether it is security relevant or not.

## License

[GPL-3.0](LICENSE)
