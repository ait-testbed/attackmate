"""
sshexecutor.py
============================================
This class enables executing commands via
ssh.
"""

from .baseexecutor import BaseExecutor, Result
from .schemas import SSHCommand
from paramiko.client import SSHClient


class SSHExecutor(BaseExecutor):
    def __init__(self, cmdconfig=None):
        self.hostname = None
        self.port = 22
        self.username = None
        self.password = None
        self.passphrase = None
        self.key_filename = None
        self.timeout = 60
        super().__init__(cmdconfig)

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

    def log_command(self, command: SSHCommand):
        self.cache_settings(command)
        self.logger.info(f"Executing SSH-Command: '{command.cmd}'")

    def _exec_cmd(self, command: SSHCommand) -> Result:
        self.cache_settings(command)
        client = SSHClient()
        client.load_system_host_keys()
        client.connect(self.hostname,
                       port=self.port,
                       username=self.username,
                       password=self.password,
                       passphrase=self.passphrase,
                       key_filename=self.key_filename,
                       timeout=self.timeout)
        stdin, stdout, stderr = client.exec_command(command.cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            return Result(error, 1)

        return Result(output, 0)
