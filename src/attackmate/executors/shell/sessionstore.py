import logging
from subprocess import Popen

from attackmate.executors.shell.ptysession import PtySession


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

    def clean_sessions(self):
        """
        Closes every pty session in the store and releases its file descriptors.

        Pipe-based sessions are left alone: they are plain ``Popen`` objects
        that are closed by the executor itself when the command finishes.
        """
        for session_name, session in self.pty_store.items():
            try:
                session.close()
                self.logger.warning(f"Closing pty for shell session '{session_name}'.")
            except Exception as e:
                self.logger.error(f"Error closing pty for shell session '{session_name}': {e}")

        self.pty_store.clear()
