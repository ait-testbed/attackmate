"""
shellexecutor.py
============================================
This class enables executing shell
commands in AttackMate.
"""

import os
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

    def open_proc(self, command: ShellCommand) -> subprocess.Popen:
        if command.session:
            return self.session_store.get_handle_by_session(command.session)

        proc = subprocess.Popen(
            [command.command_shell], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if command.creates_session:
            self.session_store.set_session(command.creates_session, proc, command.cmd)

        return proc

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
        return output.decode()

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

        return outline.decode()

    def _exec_cmd(self, command: ShellCommand) -> Result:
        try:
            proc = self.open_proc(command)
        except KeyError as e:
            raise ExecException(e)

        if command.bin:
            try:
                cmd = binascii.unhexlify(command.cmd)
                self.logger.info(
                    f"Shell-Command: Hex {command.cmd} to ascii: {bytes.fromhex(command.cmd).decode('ascii')}"
                )
            except binascii.Error:
                raise ExecException(
                    f"only hex characters are allowed in binary mode. Command: '{command.cmd}'"
                )
        else:
            cmd = command.cmd.encode('utf-8')

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
