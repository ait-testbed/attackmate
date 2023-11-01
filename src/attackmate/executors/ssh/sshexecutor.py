"""
sshexecutor.py
============================================
This class enables executing commands via
ssh.
"""

import os
from datetime import datetime
from typing import Optional
from paramiko.channel import Channel
from paramiko.client import SSHClient
from paramiko import AutoAddPolicy
from paramiko.ssh_exception import (BadHostKeyException,
                                    AuthenticationException,
                                    SSHException)
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.schemas import SFTPCommand, SSHCommand
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


class SSHExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *, varstore: VariableStore):
        self.session_store = self.SessionStore()
        self.set_defaults()
        self.timer = None
        super().__init__(pm, varstore, cmdconfig)

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
            self.port = CmdVars.variable_to_int('port', command.port)
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
            self.jmp_port = CmdVars.variable_to_int('jmp_port', command.jmp_port)
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
            raise ExecException(f'Could not get transport of SSH-Jumphost {self.jmp_hostname}')
        return sock

    def connect_use_session(self, command: SSHCommand) -> SSHClient:
        if command.session is not None:
            if not self.session_store.has_session(command.session):
                raise ExecException(f'SSH-Session not in Session-Store: {command.session}')
            else:
                return self.session_store.get_client_by_session(command.session)

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
            self.session_store.set_session(command.creates_session, client)
        return client

    def exec_sftp(self, client: SSHClient, command: SFTPCommand) -> str:
        output = ''
        if command.cmd == 'put':
            client.open_sftp().put(command.local_path, command.remote_path)
            output = f'Uploaded to {command.remote_path}'
            if command.mode:
                client.open_sftp().chmod(command.remote_path, int(command.mode, 8))
        elif command.cmd == 'get':
            client.open_sftp().get(command.remote_path, command.local_path)
            output = f'Downloaded from {command.remote_path}'
            if command.mode:
                os.chmod(command.local_path, int(command.mode, 8))
        return output

    def check_prompt(self, output: str, prompts: list[str], validate_prompt: bool = True) -> bool:
        if output and validate_prompt:
            for p in prompts:
                if output.endswith(p):
                    self.logger.debug('found prompt!')
                    return True
        return False

    def check_timer(self, seconds: int) -> bool:
        if not self.timer:
            return False

        if seconds <= 0:
            return True

        delta = datetime.now() - self.timer
        if delta.total_seconds() > seconds:
            return False
        else:
            return True

    def set_timer(self):
        self.timer = datetime.now()

    def exec_interactive_command(self, command: SSHCommand, client: SSHClient):
        channel = None

        if command.session and self.session_store.has_session(command.session):
            channel = self.session_store.get_channel_by_session(command.session)

        if not channel:
            channel = client.invoke_shell()
            if command.session:
                self.session_store.set_existing_session(command.session, client, channel)
            elif command.creates_session:
                self.session_store.set_existing_session(command.creates_session, client, channel)

        stdin = channel.makefile('wb')
        stdout = channel.makefile('rb')
        stderr = channel.makefile_stderr('rb')

        if stdin.channel.send_ready():
            stdin.write(str.encode(command.cmd))
            stdin.flush()

        return (None, stdout, stderr)

    def _exec_cmd(self, command: SSHCommand) -> Result:
        error = None
        output = ''

        if command.clear_cache:
            self.set_defaults()

        self.cache_settings(command)

        try:
            client = self.connect_use_session(command)
            if command.type == 'sftp' and isinstance(command, SFTPCommand):
                ret = self.exec_sftp(client, command)
                return Result(ret, 0)
            else:
                if command.interactive:
                    stdin, stdout, stderr = self.exec_interactive_command(command, client)
                    self.set_timer()
                    while self.check_timer(CmdVars.variable_to_int('timeout', command.command_timeout)):
                        if stdout.channel.recv_ready():
                            tmp = stdout.channel.recv(1025).decode('utf-8', 'ignore')
                            output += tmp
                            if self.check_prompt(output, command.prompts, command.validate_prompt):
                                self.timer = None
                            else:
                                self.set_timer()
                else:
                    stdin, stdout, stderr = client.exec_command(command.cmd)
                    output = stdout.read().decode('utf-8', 'ignore')
                    error = stderr.read().decode('utf-8', 'ignore')
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

        if error:
            return Result(error, 1)

        return Result(output, 0)

    class SessionStore:
        def __init__(self):
            self.store: dict[str, tuple[SSHClient, Optional[Channel]]] = {}

        def has_session(self, session_name: str) -> bool:
            if session_name in self.store:
                return True
            else:
                return False

        def get_client_by_session(self, session_name: str) -> SSHClient:
            if session_name in self.store:
                return self.store[session_name][0]
            else:
                raise KeyError('Session not found in Sessionstore')

        def get_channel_by_session(self, session_name: str) -> Optional[Channel]:
            if session_name in self.store:
                return self.store[session_name][1]
            else:
                raise KeyError('Session not found in Sessionstore')

        def get_session(self, session_name: str) -> tuple[SSHClient, Channel | None]:
            if session_name in self.store:
                return self.store[session_name]
            else:
                raise KeyError('Session not found in Sessionstore')

        def set_session(self, session_name: str, client: SSHClient, channel: Optional[Channel] = None):
            self.store[session_name] = (client, channel)

        def set_existing_session(self, session_name: str,
                                 client: SSHClient, channel: Optional[Channel] = None):
            if self.has_session(session_name):
                self.set_session(session_name, client, channel)
