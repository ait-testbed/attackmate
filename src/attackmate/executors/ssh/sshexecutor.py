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
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.executors.ssh.interactfeature import Interactive
from attackmate.result import Result
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.schemas.ssh import SFTPCommand, SSHCommand
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.executors.ssh.sessionstore import SessionStore
from attackmate.executors.ssh.sftpfeature import SFTPFeature


class SSHExecutor(BaseExecutor, SFTPFeature, Interactive):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *, varstore: VariableStore):
        self.session_store = SessionStore()
        self.set_defaults()
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

        if self.hostname is None:
            raise ExecException('No hostname set for SSH-Connection')

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
                    stdin, stdout, stderr = self.exec_interactive_command(command, client, self.session_store)
                    self.set_timer()
                    while self.check_timer(CmdVars.variable_to_int('timeout', command.command_timeout)):
                        if stdout.channel.recv_ready():
                            tmp = stdout.channel.recv(1025).decode('utf-8', 'ignore')
                            output += tmp
                            self.check_prompt(output, command.prompts, command.validate_prompt)
                else:
                    stdin, stdout, stderr = client.exec_command(command.cmd)
                    output = stdout.read().decode('utf-8', 'ignore')
                    error = stderr.read().decode('utf-8', 'ignore')
        except ValueError as e:
            raise ExecException(e)
        except AttributeError as e:
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
