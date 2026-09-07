import logging
import binascii
from datetime import datetime
from paramiko.client import SSHClient
from attackmate.schemas.ssh import SSHCommand
from attackmate.execexception import ExecException
from attackmate.executors.common.terminal import expand_keys
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.executors.ssh.sessionstore import SessionStore


class Interactive:
    def __init__(self):
        self.timer = None
        self.logger = logging.getLogger('playbook')

    def check_prompt(self, output: str, prompts: list[str]) -> bool:
        if output and prompts:
            for p in prompts:
                if output.endswith(p):
                    self.logger.debug('found prompt!')
                    self.timer = None
                    return True
        else:
            self.set_timer()
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

    def exec_interactive_command(self, command: SSHCommand, client: SSHClient, session_store: SessionStore):
        channel = None

        if command.session and session_store.has_session(command.session):
            channel = session_store.get_channel_by_session(command.session)

        if not channel:
            # Terminal type and size decide how full-screen applications draw
            # themselves, so they must be set when the shell is created.
            channel = client.invoke_shell(
                term=command.term,
                width=CmdVars.variable_to_int('pty_cols', command.pty_cols),
                height=CmdVars.variable_to_int('pty_rows', command.pty_rows),
            )
            if command.session:
                session_store.set_existing_session(command.session, client, channel)
            elif command.creates_session:
                session_store.set_existing_session(command.creates_session, client, channel)

        stdin = channel.makefile('wb')
        stdout = channel.makefile('rb')
        stderr = channel.makefile_stderr('rb')

        if stdin.channel.send_ready():
            if command.bin:
                try:
                    stdin.write(binascii.unhexlify(command.cmd))
                except binascii.Error:
                    raise ExecException(f"only hex characters are allowed in binary mode: \"{command.cmd}\"")
            else:
                cmd = expand_keys(command.cmd) if command.expand_keys else command.cmd
                stdin.write(str.encode(cmd))
            stdin.flush()

        return (None, stdout, stderr)
