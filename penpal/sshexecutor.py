"""
sshexecutor.py
============================================
This class enables executing commands via
ssh.
"""

from paramiko.client import SSHClient
from paramiko import AutoAddPolicy
from paramiko.ssh_exception import (BadHostKeyException,
                                    AuthenticationException,
                                    SSHException)
from .baseexecutor import BaseExecutor, ExecException, Result
from .schemas import SSHCommand


class SSHExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None):
        self.session_store = {}
        self.set_defaults()
        super().__init__(cmdconfig)

    def set_defaults(self):
        self.hostname = None
        self.port = 22
        self.username = None
        self.password = None
        self.passphrase = None
        self.key_filename = None
        self.timeout = 60
        self.jmp_hostname = None
        self.jmp_port = 22
        self.jmp_username = self.username

    def cache_settings(self, command: SSHCommand):
        if command.hostname:
            self.hostname = command.hostname
        if command.port:
            self.port = command.port
        if command.username:
            self.username = command.username
        if command.password:
            self.password = command.password
        if command.passphrase:
            self.passphrase = command.passphrase
        if command.key_filename:
            self.key_filename = command.key_filename
        if command.timeout:
            self.timeout = command.timeout
        if command.jmp_hostname:
            self.jmp_hostname = command.jmp_hostname
        if command.jmp_port:
            self.jmp_port = command.jmp_port
        if command.jmp_username:
            self.jmp_username = command.jmp_username

    def log_command(self, command: SSHCommand):
        self.cache_settings(command)
        self.logger.info(f"Executing SSH-Command: '{command.cmd}'")

    def connect_jmphost(self, command: SSHCommand):
        jmp = SSHClient()
        jmp.load_system_host_keys()
        jmp.set_missing_host_key_policy(AutoAddPolicy())

        kwargs = dict(
            hostname=self.jmp_hostname,
            port=self.jmp_port,
            username=self.jmp_username,
            password=self.password,
            passphrase=self.passphrase,
            key_filename=self.key_filename,
            timeout=self.timeout,
        )

        jmp.connect(**kwargs)
        transport = jmp.get_transport()
        if transport:
            sock = transport.open_channel(
                    'direct-tcpip', (self.hostname, self.port), ('', 0)
            )
        else:
            raise ExecException(f"Could not get transport of SSH-Jumphost {self.jmp_hostname}")
        return sock

    def connect_use_session(self, command: SSHCommand):
        if command.session is not None:
            if command.session not in self.session_store:
                raise ExecException(f"SSH-Session not in Session-Store: {command.session}")
            else:
                return self.session_store[command.session]

        jmp_sock = None
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())

        if self.jmp_hostname is not None:
            jmp_sock = self.connect_jmphost(command)

        kwargs = dict(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password,
            passphrase=self.passphrase,
            key_filename=self.key_filename,
            timeout=self.timeout,
            sock=jmp_sock
        )
        client.connect(**kwargs)
        if command.creates_session is not None:
            self.session_store[command.creates_session] = client
        return client

    def _exec_cmd(self, command: SSHCommand) -> Result:
        if command.clear_cache:
            self.set_defaults()
        else:
            self.cache_settings(command)
        try:
            client = self.connect_use_session(command)
            stdin, stdout, stderr = client.exec_command(command.cmd)
        except ValueError as e:
            raise ExecException(e)
        except BadHostKeyException as e:
            raise ExecException(e)
        except AuthenticationException as e:
            raise ExecException(e)
        except OSError as e:
            raise ExecException(e)
        except SSHException as e:
            raise ExecException(e)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            return Result(error, 1)

        return Result(output, 0)
