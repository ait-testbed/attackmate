"""
shellexecutor.py
============================================
This class enables executing shell
commands in AttackMate.
"""

import os
import platform
import subprocess
from subprocess import TimeoutExpired
from datetime import datetime
import binascii
from attackmate.execexception import ExecException
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.shell import ShellCommand
from attackmate.schemas.config import CommandConfig
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.executors.common.terminal import expand_keys, render_output
from attackmate.executors.shell.ptysession import PtySession
from attackmate.executors.shell.sessionstore import SessionStore
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.executors.executor_factory import executor_factory


@executor_factory.register_executor('shell')
class ShellExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, varstore: VariableStore, cmdconfig=CommandConfig()):
        self.session_store = SessionStore()
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: BaseCommand):
        self.logger.info(f"Executing Shell-Command: '{command.cmd}'")

    def cleanup(self):
        self.session_store.clean_sessions()

    def open_proc(self, command: ShellCommand) -> subprocess.Popen:
        if command.session:
            return self.session_store.get_handle_by_session(command.session)

        proc = subprocess.Popen(
            [command.command_shell], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if command.creates_session:
            self.session_store.set_session(command.creates_session, proc, command.cmd)

        return proc

    def open_pty(self, command: ShellCommand) -> PtySession:
        """Return the pty session for *command*, creating one if needed.

        Kept separate from :meth:`open_proc` so the pipe-based path is not
        touched by pty support at all.
        """
        if command.session:
            session = self.session_store.get_pty_by_session(command.session)
            if not session.is_alive():
                raise ExecException(f"Shell-Session '{command.session}' has exited")
            return session

        session = PtySession(
            command_shell=command.command_shell,
            rows=CmdVars.variable_to_int('pty_rows', command.pty_rows),
            cols=CmdVars.variable_to_int('pty_cols', command.pty_cols),
            term=command.term,
            screen=command.screen,
        )

        if command.creates_session:
            self.session_store.set_pty_session(command.creates_session, session)

        return session

    def encode_cmd(self, command: ShellCommand) -> bytes:
        """Turn ``command.cmd`` into the bytes to send.

        Key expansion produces a local copy rather than writing back to
        ``command.cmd``: the JSON audit log serialises the command *after* it
        ran, and Looper re-executes the same object, so mutating it would both
        record raw control bytes and expand twice on the second pass.
        """
        if command.bin:
            try:
                cmd = binascii.unhexlify(command.cmd)
                self.logger.info(
                    f"Shell-Command: Hex {command.cmd} to ascii: {bytes.fromhex(command.cmd).decode('ascii')}"
                )
                return cmd
            except binascii.Error:
                raise ExecException(
                    f"only hex characters are allowed in binary mode. Command: '{command.cmd}'"
                )

        text = expand_keys(command.cmd) if command.expand_keys else command.cmd
        return text.encode('utf-8')

    def exec_pty(self, command: ShellCommand) -> Result:
        """Run a command through a pseudo-terminal."""
        try:
            session = self.open_pty(command)
        except KeyError as e:
            raise ExecException(e)

        cmd = self.encode_cmd(command)
        self.logger.debug('Running command in a pty')
        session.drain()
        session.write(cmd)

        output = ''
        if command.read:
            raw = session.read(
                idle_timeout=CmdVars.variable_to_int('timeout', command.command_timeout),
                prompts=command.prompts,
            )
            # session.screen, not command.screen: whether a session emulates a
            # screen is fixed when it is created, so a later command on the
            # same session cannot turn it on retroactively.
            output = render_output(raw, screen=session.screen)

        if not command.session and not command.creates_session:
            session.close()

        return Result(output, 0)

    def popen_close(self, proc):
        self.logger.debug('Closing popen process')
        proc.terminate()
        proc.wait(timeout=10)

    @staticmethod
    def non_block_read(stdout):
        fd = stdout.fileno()
        try:
            import fcntl

            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        except ImportError:
            raise ExecException("The 'fcntl' module is not available. This module requires a Unix-like OS.")
        try:
            return stdout.read()
        except Exception:
            return b''

    def popen_noninteractive(self, proc: subprocess.Popen, cmd: bytes, timeout=None) -> str:
        self.logger.debug('Running non interactive command')
        try:
            output, error = proc.communicate(cmd, timeout=timeout)
        except TimeoutExpired:
            self.logger.info('Timeout of noninteractive shell command expired')
            proc.kill()
            output, error = proc.communicate()
        output += error
        # Command output is arbitrary bytes, not guaranteed UTF-8. A strict decode
        # raises UnicodeDecodeError, which nothing between here and main() catches -
        # so one undecodable byte terminates the whole playbook rather than failing
        # this step. Replace undecodable bytes instead: output is used for logging,
        # error_if matching and save-to-file, none of which need a lossless
        # round-trip.
        return output.decode(errors='replace')

    def popen_interactive(
        self, proc: subprocess.Popen, cmd: bytes, timeout: int = 5, read: bool = True
    ) -> str:
        self.logger.debug('Running interactive command')

        self.logger.debug(f'Sending command: {cmd.decode("utf-8")}')

        if proc.stdin:
            proc.stdin.write(cmd)
            proc.stdin.flush()

        outline = b''
        if read:
            begin = datetime.now()
            while (datetime.now() - begin).total_seconds() < timeout:
                tmp = self.non_block_read(proc.stdout)
                if tmp:
                    outline += tmp
                    begin = datetime.now()  # reset timer when data comes

        # Same reasoning as popen_noninteractive: never let output bytes end the run.
        return outline.decode(errors='replace')

    async def _exec_cmd(self, command: ShellCommand) -> Result:
        if command.pty:
            if platform.system() == 'Windows':
                return Result('Pseudo-terminals are only available on Unix-like systems!', 1)
            return self.exec_pty(command)

        try:
            proc = self.open_proc(command)
        except KeyError as e:
            raise ExecException(e)

        cmd = self.encode_cmd(command)

        timeout = CmdVars.variable_to_int('timeout', command.command_timeout)
        output = ''

        if command.interactive:
            output = self.popen_interactive(proc, cmd, timeout, read=command.read)
            if not command.session and not command.creates_session:
                self.popen_close(proc)
        else:
            output = self.popen_noninteractive(proc, cmd)
            self.popen_close(proc)

        return Result(output, 0)
