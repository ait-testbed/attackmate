from paramiko.channel import Channel
from paramiko.client import SSHClient
from typing import Optional
import logging


class SessionStore:
    def __init__(self):
        self.store: dict[str, tuple[SSHClient, Optional[Channel]]] = {}
        self.logger = logging.getLogger('playbook')

    def __getstate__(self):
        """
        store contains the states of the ssh connections. they are not
        serializable.
        """
        state = self.__dict__.copy()
        state['store'] = None
        return state

    def has_session(self, session_name: str) -> bool:
        if session_name in self.store:
            return True
        else:
            return False

    def get_client_by_session(self, session_name: str) -> SSHClient:
        if session_name in self.store:
            return self.store[session_name][0]
        else:
            raise KeyError('Session not found in Sessionstore')

    def get_channel_by_session(self, session_name: str) -> Optional[Channel]:
        if session_name in self.store:
            return self.store[session_name][1]
        else:
            raise KeyError('Session not found in Sessionstore')

    def get_session(self, session_name: str) -> tuple[SSHClient, Channel | None]:
        if session_name in self.store:
            return self.store[session_name]
        else:
            raise KeyError('Session not found in Sessionstore')

    def set_session(self, session_name: str, client: SSHClient, channel: Optional[Channel] = None):
        self.store[session_name] = (client, channel)

    def set_existing_session(self, session_name: str,
                             client: SSHClient, channel: Optional[Channel] = None):
        if self.has_session(session_name):
            self.set_session(session_name, client, channel)


    def clean_sessions(self):
        """
        Closes all active SSH sessions and their associated channels in the session store,
        then removes all entries from the store.
        """
        for session_name, (client, channel) in self.store.items():
            if channel is not None:
                try:
                    channel.close()
                    self.logger.warning(f"Closing channel for ssh session '{session_name}'.")

                except Exception as e:
                    self.logger.error(f"Error closing channel for ssh session '{session_name}': {e}")

            if client is not None:
                try:
                    client.close()
                    self.logger.warning(f"Closing client for ssh session '{session_name}'")

                except Exception as e:
                    self.logger.error(f"Error closing client for ssh session '{session_name}': {e}")

        self.store.clear()

