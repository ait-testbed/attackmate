from vncdotool.api import ThreadedVNCClientProxy as VncClient


class SessionStore:
    def __init__(self):
        self.store: dict[str, VncClient] = {}

    def has_session(self, session_name: str) -> bool:
        return session_name in self.store

    def get_client_by_session(self, session_name: str) -> VncClient:
        if session_name in self.store:
            return self.store[session_name]
        else:
            raise KeyError('Session not found in Sessionstore')

    def set_session(self, session_name: str, client: VncClient):
        self.store[session_name] = client

    def remove_session(self, session_name: str):
        if session_name in self.store:
            del self.store[session_name]
        else:
            raise KeyError('Session not found in Sessionstore')

    def clean_sessions(self):
        """
        Disconnect all active vnc sessionsin the session store,
        """
        for session_name, client in self.store.items():
            if client is not None:
                try:
                    client.disconnect()
                except Exception as e:
                    self.logger.error(f"Error closing vnc client for session '{session_name}': {e}")

        self.store.clear()

