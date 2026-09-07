"""
ptysession.py
============================================
A local shell running behind a pseudo-terminal.

The default ``shell`` executor connects the shell to pipes. Programs that
insist on a terminal therefore fail: ``vim`` and ``nano`` refuse to draw a
screen, and ``sudo`` cannot prompt for a password because it reads from
``/dev/tty`` rather than from stdin. Giving the shell a pseudo-terminal
removes that restriction.
"""

import logging
import os
import select
import signal
import struct
import subprocess
from datetime import datetime
from typing import List, Optional

from attackmate.execexception import ExecException
from attackmate.executors.common.terminal import PROMPT_TAIL, TerminalScreen, strip_ansi

# fcntl, pty and termios exist only on Unix. They are imported where they are
# used rather than here, so that importing attackmate keeps working on Windows -
# the same reason shellexecutor.non_block_read imports fcntl inside the function.

# Reading in large chunks keeps up with the redraw bursts of full-screen
# applications without spinning on tiny reads.
READ_CHUNK = 65536

# How long to wait for the shell's startup prompt before the first command.
STARTUP_DRAIN = 0.3

# How long a shell gets to exit after its terminal is hung up, before SIGKILL.
HANGUP_GRACE = 5


class PtySession:
    """A shell process attached to a pseudo-terminal.

    Parameters
    ----------
    command_shell : str
        Shell to spawn, e.g. ``/bin/sh``.
    rows : int, optional
        Terminal height reported to the child. Defaults to ``24``.
    cols : int, optional
        Terminal width reported to the child. Defaults to ``80``.
    term : str, optional
        Value of ``TERM`` for the child. Defaults to ``xterm-256color``.
    screen : bool, optional
        Emulate a terminal screen so full-screen applications can be read
        back as the text they display. Defaults to ``False``.
    """

    def __init__(
        self,
        command_shell: str = '/bin/sh',
        rows: int = 24,
        cols: int = 80,
        term: str = 'xterm-256color',
        screen: bool = False,
    ):
        import pty

        self.logger = logging.getLogger('playbook')
        self.rows = rows
        self.cols = cols
        self.master_fd, slave_fd = pty.openpty()
        self.set_winsize(rows, cols)

        env = os.environ.copy()
        env['TERM'] = term
        env['LINES'] = str(rows)
        env['COLUMNS'] = str(cols)

        try:
            self.proc = subprocess.Popen(
                [command_shell],
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                env=env,
                close_fds=True,
                preexec_fn=self._make_controlling_terminal,
            )
        finally:
            # The child holds its own copy; keeping ours open would stop reads
            # from ever reporting EOF after the shell exits.
            os.close(slave_fd)

        self.screen: Optional[TerminalScreen] = TerminalScreen(rows, cols) if screen else None
        self.closed = False

        # A shell prints its prompt as soon as it starts. Left in the buffer,
        # that prompt would satisfy the prompt check of the first read before
        # the first command had produced any output at all.
        self.read(idle_timeout=STARTUP_DRAIN)

    @staticmethod
    def _make_controlling_terminal():
        """Make the inherited pty the controlling terminal of the child.

        Runs in the forked child before ``exec``. Without a controlling
        terminal the shell disables job control and ``/dev/tty`` is
        unavailable, which is exactly what breaks ``sudo``.
        """
        import fcntl
        import termios

        os.setsid()
        try:
            fcntl.ioctl(0, termios.TIOCSCTTY, 0)
        except OSError:
            # Some platforms attach the terminal on setsid() already.
            pass

    def set_winsize(self, rows: int, cols: int) -> None:
        """Report a terminal size of *rows* x *cols* to the child."""
        import fcntl
        import termios

        try:
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
        except OSError as e:
            self.logger.debug(f'Could not set pty window size: {e}')

    def write(self, data: bytes) -> None:
        """Send *data* to the terminal as if it had been typed."""
        if self.closed:
            raise ExecException('Cannot write to a closed pty session')
        os.write(self.master_fd, data)

    def drain(self) -> bytes:
        """Consume output that is already waiting, without blocking.

        Called before sending a command so that the previous command's
        trailing prompt cannot end the next command's read immediately.
        """
        pending = b''
        while not self.closed:
            try:
                readable, _, _ = select.select([self.master_fd], [], [], 0)
            except (OSError, ValueError):
                break
            if not readable:
                break
            try:
                chunk = os.read(self.master_fd, READ_CHUNK)
            except OSError:
                break
            if not chunk:
                break
            pending += chunk
            if self.screen is not None:
                self.screen.feed(chunk)
        return pending

    def read(
        self,
        idle_timeout: float,
        prompts: Optional[List[str]] = None,
        max_wait: Optional[float] = None,
    ) -> bytes:
        """Read output until it goes quiet, a prompt appears, or time runs out.

        Parameters
        ----------
        idle_timeout : float
            Seconds without new output after which reading stops. A value of
            ``0`` or less means "no time limit": reading then continues until a
            prompt matches, matching what ``command_timeout: 0`` already means
            for ssh commands (see ``Interactive.check_timer``). Combining it
            with an empty *prompts* would never return, so it is rejected.
        prompts : list of str, optional
            Reading stops early once the output ends with one of these.
        max_wait : float, optional
            Hard upper bound on the total time spent reading. Off by default:
            capping at some multiple of *idle_timeout* would silently truncate
            any command that legitimately streams output for longer, which is
            invisible from the playbook. Silence still ends the read through
            *idle_timeout*, matching what ``popen_interactive`` does for pipes.

        Returns
        -------
        bytes
            Everything read during this call. Also fed to the emulated
            screen when the session has one.
        """
        wait_for_prompt_only = idle_timeout <= 0
        if wait_for_prompt_only and not prompts:
            raise ExecException(
                'command_timeout 0 waits for a prompt, so at least one entry in '
                "'prompts' is required. Set a timeout or define prompts."
            )
        buffer = b''
        started = datetime.now()
        last_data = datetime.now()

        while True:
            now = datetime.now()
            if max_wait is not None and (now - started).total_seconds() >= max_wait:
                self.logger.debug('pty read stopped: maximum wait reached')
                break
            if not wait_for_prompt_only and (now - last_data).total_seconds() >= idle_timeout:
                break

            try:
                readable, _, _ = select.select([self.master_fd], [], [], 0.05)
            except (OSError, ValueError):
                break
            if not readable:
                continue

            try:
                chunk = os.read(self.master_fd, READ_CHUNK)
            except OSError:
                # The child exited and closed the other end of the pty.
                break
            if not chunk:
                break

            buffer += chunk
            last_data = datetime.now()
            if self.screen is not None:
                self.screen.feed(chunk)
            if prompts and self._ends_with_prompt(buffer[-PROMPT_TAIL:], prompts):
                self.logger.debug('pty read stopped: found prompt')
                break

        return buffer

    @staticmethod
    def _ends_with_prompt(buffer: bytes, prompts: List[str]) -> bool:
        # Prompts are matched against readable text: a shell prompt is usually
        # followed by colour and cursor sequences that would defeat endswith().
        text = strip_ansi(buffer.decode(errors='replace')).rstrip('\n')
        return any(text.endswith(prompt) for prompt in prompts)

    def is_alive(self) -> bool:
        """Return ``True`` while the shell process is still running."""
        return not self.closed and self.proc.poll() is None

    def close(self) -> None:
        """Terminate the shell and release the pseudo-terminal.

        Closing the master side first is what makes this quick. A shell with a
        controlling terminal is an interactive shell, and an interactive shell
        ignores SIGTERM - so signalling it first meant waiting out the timeout
        on every single session before falling back to SIGKILL. Dropping our
        end of the terminal instead hangs it up, which is the condition a shell
        does exit on.
        """
        if self.closed:
            return
        self.closed = True

        try:
            os.close(self.master_fd)
        except OSError:
            pass

        try:
            if self.proc.poll() is None:
                try:
                    self.proc.wait(timeout=HANGUP_GRACE)
                except subprocess.TimeoutExpired:
                    # Still there: signal the whole group, so that whatever the
                    # shell started (an editor, a pager) goes down with it.
                    self._signal_group(signal.SIGKILL)
                    self.proc.wait(timeout=HANGUP_GRACE)
        except Exception as e:
            self.logger.debug(f'Error while closing pty session: {e}')

    def _signal_group(self, sig: int) -> None:
        try:
            os.killpg(os.getpgid(self.proc.pid), sig)
        except (ProcessLookupError, PermissionError, OSError):
            self.proc.kill()
