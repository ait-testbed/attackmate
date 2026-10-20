"""
shellexecutor.py
============================================
This class enables executing shell
commands in AttackMate.
"""

import os
import platform
import time
from typing import Optional
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
from attackmate.executors.common.terminal import (PROMPT_TAIL, append_exit_marker,
                                                  expand_keys, make_exit_marker,
                                                  render_output, split_exit_marker)
from attackmate.executors.shell.ptysession import PtySession
from attackmate.executors.shell.sessionstore import SessionStore
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.executors.executor_factory import executor_factory

# How long to wait between polls of a pipe-based interactive session. Without
# it the read loop spins on a core for the whole timeout.
POLL_INTERVAL = 0.05


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
            proc = self.session_store.get_handle_by_session(command.session)
            if proc.poll() is not None:
                # Writing to a shell that has exited raises BrokenPipeError,
                # which nothing catches - it ends the playbook. That is how a
                # dropped reverse shell presents, so it needs to be a normal
                # command failure rather than a crash.
                raise ExecException(f"Shell-Session '{command.session}' has exited")
            return proc

        proc = subprocess.Popen(
            [command.command_shell],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # A session outlives the command that created it, so it has to be
            # terminated by name at the end of the run - and killing a shell
            # does not kill what it started. Giving a session its own process
            # group is what lets the store signal the whole tree later. Without
            # it the session shares AttackMate's group and signalling it would
            # take AttackMate down too.
            start_new_session=bool(command.creates_session),
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
            raw=command.raw,
        )

        if command.creates_session:
            self.session_store.set_pty_session(command.creates_session, session)

        return session

    def encode_cmd(self, command: ShellCommand, exit_marker: Optional[str] = None) -> bytes:
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
        if exit_marker is not None:
            text = append_exit_marker(text, exit_marker)
        return text.encode('utf-8')

    def exec_pty(self, command: ShellCommand) -> Result:
        """Run a command through a pseudo-terminal."""
        try:
            session = self.open_pty(command)
        except KeyError as e:
            raise ExecException(e)

        # Generated here rather than stored on the command: the audit log
        # serialises the command's attributes, so anything parked on it leaks
        # into the artifact.
        marker = make_exit_marker() if command.wait_for_exit else None
        cmd = self.encode_cmd(command, exit_marker=marker)
        self.logger.debug('Running command in a pty')
        session.drain()
        session.write(cmd)

        output = ''
        exit_status = None
        if command.read:
            # Stop on the marker rather than on a prompt or a silence: a
            # script that prints nothing for minutes is not finished, and a
            # prompt is not something every program gives you.
            raw = session.read(
                idle_timeout=(0 if command.wait_for_exit
                              else CmdVars.variable_to_int('timeout', command.command_timeout)),
                prompts=command.prompts,
                max_wait=self.read_timeout(command),
                stop_when_contains=marker,
            )
            # session.screen, not command.screen: whether a session emulates a
            # screen is fixed when it is created, so a later command on the
            # same session cannot turn it on retroactively.
            output = render_output(raw, screen=session.screen)
            if marker is not None:
                output, exit_status = split_exit_marker(output, marker)

        if not command.session and not command.creates_session:
            session.close()

        return self.build_result(command, output, exit_status)

    @staticmethod
    def read_timeout(command: ShellCommand):
        """Total time bound for one read, distinct from the idle command_timeout."""
        if command.read_timeout is None:
            return None
        return CmdVars.variable_to_int('read_timeout', command.read_timeout)

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
        self, proc: subprocess.Popen, cmd: bytes, timeout: int = 5, read: bool = True,
        stop_when_contains: Optional[str] = None, max_wait: Optional[float] = None,
    ) -> str:
        self.logger.debug('Running interactive command')

        self.logger.debug(f'Sending command: {cmd.decode("utf-8")}')

        if proc.stdin:
            try:
                proc.stdin.write(cmd)
                proc.stdin.flush()
            except (BrokenPipeError, ValueError) as e:
                # The session died between the liveness check and this write -
                # poll() can still report a process alive for a moment after it
                # is killed. Uncaught, this ended the whole playbook.
                raise ExecException(f'Shell-Session is no longer accepting input: {e}')

        outline = b''
        if read:
            # With a marker to wait for, the idle timeout does not apply: a
            # command that has gone quiet has not necessarily finished, which
            # is the whole point of waiting for one.
            wait_for_marker = stop_when_contains is not None
            started = datetime.now()
            begin = datetime.now()
            while wait_for_marker or (datetime.now() - begin).total_seconds() < timeout:
                if max_wait is not None and (datetime.now() - started).total_seconds() >= max_wait:
                    self.logger.debug('interactive read stopped: maximum wait reached')
                    break

                tmp = self.non_block_read(proc.stdout)
                if tmp:
                    outline += tmp
                    begin = datetime.now()  # reset timer when data comes
                    # Only the tail can hold a marker that has just arrived.
                    # Decoding the whole buffer each time would be quadratic on
                    # a command with a lot of output.
                    tail = outline[-PROMPT_TAIL:].decode(errors='replace')
                    if wait_for_marker and stop_when_contains in tail:
                        self.logger.debug('interactive read stopped: found marker')
                        break
                    continue

                if wait_for_marker and proc.poll() is not None:
                    # The shell exited without ever printing the marker, so no
                    # more output is coming and waiting longer cannot help.
                    self.logger.debug('interactive read stopped: session ended')
                    break
                # Without this the loop spins on a core for the whole timeout.
                time.sleep(POLL_INTERVAL)

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

        # Only the interactive path needs a marker. A non-interactive command
        # is run with communicate(), which already waits for the process to
        # finish and yields its real status - so rewriting the command there
        # would buy nothing.
        marker = make_exit_marker() if command.wait_for_exit and command.interactive else None
        cmd = self.encode_cmd(command, exit_marker=marker)

        timeout = CmdVars.variable_to_int('timeout', command.command_timeout)
        output = ''

        exit_status = None

        if command.interactive:
            output = self.popen_interactive(
                proc, cmd, timeout, read=command.read,
                stop_when_contains=marker, max_wait=self.read_timeout(command),
            )
            if marker is not None:
                output, exit_status = split_exit_marker(output, marker)
            if not command.session and not command.creates_session:
                self.popen_close(proc)
        else:
            output = self.popen_noninteractive(proc, cmd)
            # communicate() has already reaped the process, so this is the real
            # status of the command. It was simply discarded before.
            exit_status = proc.returncode
            self.popen_close(proc)

        return self.build_result(command, output, exit_status)
