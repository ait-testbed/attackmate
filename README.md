# PenPal

PenPal is an attack orchestration tool that executes full attack-chains based on playbooks.

![PenPal Schema](images/penpal-schema.png "PenPal Schema")

# Requirements

PenPal can use Metasploit-Module. For this feature it is
required to start the Metasploit-RPC-Daemon:

```
msfrpcd -P securepassword
```

# Installation

```
$ pip3 install -e .
```

# Execute

```
$ penpal --config playbook.yml
```

# Documentation

Please take a look at our documentation for how to install and use penpal:

* [Installation](https://aeciddocs.ait.ac.at/penpal/current/readme_link.html#)
* [Configuration](https://aeciddocs.ait.ac.at/penpal/current/configuration/configuration.html)
* [Documentation](https://aeciddocs.ait.ac.at/penpal)

## Security

If you discover any security-related issues read the [SECURITY.md](/SECURITY.md) first and report the issues.

## License

[GPL-3.0](LICENSE)
