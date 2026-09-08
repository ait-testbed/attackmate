from paramiko.channel import Channel
from paramiko.client import SSHClient
from typing import Any, Optional
import logging


class SessionStore:
    def __init__(self):
        self.store: dict[str, tuple[SSHClient, Optional[Channel]]] = {}
        # Screen state has to survive between commands: a full-screen program
        # draws once and then only sends the parts that change, so rendering
        # each command's output on its own would show fragments.
        self.screens: dict[str, Any] = {}
        self.logger = logging.getLogger('playbook')

    def get_screen(self, session_name: Optional[str], rows: int, cols: int):
        """Return the terminal screen for *session_name*, creating it if needed.

        Commands without a session get a throwaway screen, since there is no
        later command that could observe its state.
        """
        from attackmate.executors.common.terminal import TerminalScreen

        if session_name is None:
            return TerminalScreen(rows, cols)
        if session_name not in self.screens:
            self.screens[session_name] = TerminalScreen(rows, cols)
        return self.screens[session_name]

    def __getstate__(self):
        """
        store contains the states of the ssh connections. they are not
        serializable.
        """
        state = self.__dict__.copy()
        state['store'] = None
        state['screens'] = None
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
        self.screens.clear()

    def session_is_alive(self, session_name: str) -> bool:
        """True if the stored client still has an active transport."""
        if session_name not in self.store:
            return False
        client, _ = self.store[session_name]
        transport = client.get_transport() if client else None
        return bool(transport and transport.is_active())

    def close_session(self, session_name: str) -> bool:
        """Close one session by name, and forget its terminal screen.

        The screen has to go with it, or a later session reusing the name
        inherits the old one's contents.
        """
        if session_name not in self.store:
            return False
        client, channel = self.store.pop(session_name)
        self.screens.pop(session_name, None)
        for closeable in (channel, client):
            try:
                if closeable is not None:
                    closeable.close()
            except Exception as e:
                self.logger.error(f"Error closing ssh session '{session_name}': {e}")
        return True
