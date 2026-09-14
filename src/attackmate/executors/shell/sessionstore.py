import logging
import os
import signal
import time
from subprocess import Popen, TimeoutExpired

from attackmate.executors.shell.ptysession import HANGUP_GRACE, PtySession


class SessionStore:
    def __init__(self):
        self.store: dict[str, tuple[Popen, str]] = {}
        self.pty_store: dict[str, PtySession] = {}
        self.logger = logging.getLogger('playbook')

    def __getstate__(self):
        """
        Background commands are dispatched with a 'spawn' multiprocessing context,
        which pickles the executor - and with it this store. Neither a Popen nor a
        PtySession survives that: both own file objects and locks, so pickling one
        raises "cannot pickle '_thread.lock' object" and the background command
        fails before it starts. The child cannot use a parent's session anyway,
        so drop both stores instead of trying to transport them.

        Emptied rather than set to None: a child that still looks a session up
        then gets the normal KeyError, which becomes an ExecException, instead
        of "argument of type 'NoneType' is not iterable" from a membership test.
        """
        state = self.__dict__.copy()
        state['store'] = {}
        state['pty_store'] = {}
        return state

    def has_session(self, session_name: str) -> bool:
        if session_name in self.store:
            return True
        else:
            return False

    def get_handle_by_session(self, session_name: str) -> Popen:
        if session_name in self.store:
            return self.store[session_name][0]
        else:
            raise KeyError('Session not found in Sessionstore')

    def get_command_by_session(self, session_name: str) -> str:
        if session_name in self.store:
            return self.store[session_name][1]
        else:
            raise KeyError('Session not found in Sessionstore')

    def get_session(self, session_name: str) -> tuple[Popen, str]:
        if session_name in self.store:
            return self.store[session_name]
        else:
            raise KeyError('Session not found in Sessionstore')

    def set_session(self, session_name: str, handle: Popen, command: str):
        self.store[session_name] = (handle, command)

    def set_existing_session(self, session_name: str,
                             handle: Popen, command: str):
        if self.has_session(session_name):
            self.set_session(session_name, handle, command)

    def has_pty_session(self, session_name: str) -> bool:
        return session_name in self.pty_store

    def get_pty_by_session(self, session_name: str) -> PtySession:
        if session_name in self.pty_store:
            return self.pty_store[session_name]
        else:
            raise KeyError('Session not found in Sessionstore')

    def set_pty_session(self, session_name: str, session: PtySession):
        self.pty_store[session_name] = session

    def _signal_group(self, pgid: int, sig: int):
        """Signal a session's whole process group, tolerating an empty group."""
        try:
            os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError, OSError):
            # The group is already gone, or is not ours to signal.
            pass

    def close_pipe_session(self, session_name: str, proc: Popen):
        """Terminate one pipe-based session and everything it started.

        The executor closes an ordinary command's process, but deliberately not
        a session's - a session has to stay open for the commands that follow.
        Nothing closed it afterwards either, so a session that left a listener
        or a shell running kept it alive after AttackMate exited, holding its
        port and corrupting the next run.

        Killing the shell alone is not enough, because what the session started
        is a child of it. Sessions are created with ``start_new_session=True``
        (see ``ShellExecutor.open_proc``), so signalling the process group takes
        the whole tree down.
        """
        # start_new_session makes the shell its own group leader, so its pid is
        # the group id. Captured before anything can reap it.
        pgid = proc.pid
        try:
            if proc.stdin and not proc.stdin.closed:
                # Ends a shell that is blocked reading its next command.
                proc.stdin.close()

            self._signal_group(pgid, signal.SIGTERM)

            deadline = time.monotonic() + HANGUP_GRACE
            while proc.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)

            # Sweep the group even when the shell exited cleanly. That is the
            # leak: `nc -l &` keeps running after its parent shell is gone, and
            # waiting on the shell alone reports success while the listener
            # still holds the port.
            self._signal_group(pgid, signal.SIGKILL)

            if proc.poll() is None:
                proc.kill()
            try:
                proc.wait(timeout=HANGUP_GRACE)
            except TimeoutExpired:
                self.logger.error(f"Shell session '{session_name}' did not terminate")
        finally:
            for stream in (proc.stdout, proc.stderr):
                try:
                    if stream:
                        stream.close()
                except OSError:
                    pass

    def clean_sessions(self):
        """Close every session in the store and release its resources."""
        for session_name, session in self.pty_store.items():
            try:
                session.close()
                self.logger.warning(f"Closing pty for shell session '{session_name}'.")
            except Exception as e:
                self.logger.error(f"Error closing pty for shell session '{session_name}': {e}")

        for session_name, (proc, _) in self.store.items():
            try:
                self.close_pipe_session(session_name, proc)
                self.logger.warning(f"Closing shell session '{session_name}'.")
            except Exception as e:
                self.logger.error(f"Error closing shell session '{session_name}': {e}")

        self.pty_store.clear()
        self.store.clear()

    def session_exists(self, session_name: str) -> bool:
        """True if a session of either kind is stored under this name."""
        return session_name in self.store or session_name in self.pty_store

    def session_is_alive(self, session_name: str) -> bool:
        """True if the stored session's shell is still running."""
        if session_name in self.pty_store:
            return self.pty_store[session_name].is_alive()
        if session_name in self.store:
            return self.store[session_name][0].poll() is None
        return False

    def close_session(self, session_name: str) -> bool:
        """Close one session by name, whichever kind it is.

        Returns False if no such session is stored, so a playbook can close a
        foothold it is finished with without having to know it still exists.
        """
        if session_name in self.pty_store:
            self.pty_store.pop(session_name).close()
            return True
        if session_name in self.store:
            proc, _ = self.store.pop(session_name)
            self.close_pipe_session(session_name, proc)
            return True
        return False
