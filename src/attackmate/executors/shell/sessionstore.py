from subprocess import Popen


class SessionStore:
    def __init__(self):
        self.store: dict[str, tuple[Popen, str]] = {}

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
