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

## License

[GPL-3.0](LICENSE)
