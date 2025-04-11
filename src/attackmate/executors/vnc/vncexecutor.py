"""
vncexecutor.py
============================================
This class enables executing commands via vnc.
It utilizes the vncdotool. https://github.com/sibson/vncdotool (can be installed with pip)

the vnc client connection_string needs to be in the format address[:display|::port]

"""

from typing import Optional, Union
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.schemas.vnc import VncCommand
from vncdotool import api
from vncdotool.client import AuthenticationError
from attackmate.executors.vnc.sessionstore import SessionStore
from attackmate.executors.executor_factory import executor_factory
import time


@executor_factory.register_executor('vnc')
class VncExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *, varstore: VariableStore):
        self.session_store = SessionStore()
        self.connection_timeout = 60
        self.set_defaults()
        super().__init__(pm, varstore, cmdconfig)

    def set_defaults(self):
        self.hostname = None
        self.port = None
        self.display = None
        self.password = None

    def build_connection_string(
        self,
        hostname: Optional[str],
        port: Optional[Union[int, str]] = None,
        display: Optional[Union[int, str]] = None,
    ) -> str:
        if not hostname:
            raise ExecException('Hostname is required for VNC connection.')
        connection_str = hostname
        if display is not None:
            connection_str += f":{display}"
        elif port is not None:
            connection_str += f"::{port}"
        return connection_str

    def connect(self, command: VncCommand) -> api.ThreadedVNCClientProxy:
        connection_string = self.build_connection_string(
            command.hostname, command.port, command.display
        )
        if command.password is None:
            client = api.connect(connection_string, timeout=command.expect_timeout)
        else:
            client = api.connect(
                connection_string, command.password, timeout=command.expect_timeout
            )
        start_time = time.time()
        while time.time() - start_time < self.connection_timeout:
            if client and client.protocol and client.protocol.connected:
                self.logger.info(f"Connected to VNC server: {connection_string}")
                return client
            time.sleep(0.1)  # Poll every 100ms for connection status
        self.logger.info(f"Could not connect to VNC server: {connection_string}")
        client.disconnect()
        return None

    def connect_use_session(self, command):

        if command.creates_session is not None:
            # If 'creates_session' is specified, create a new session and save it
            client = self.connect(command)
            if not client:
                return None
            self.session_store.set_session(command.creates_session, client)
            return client

        if command.session is not None:
            # If 'session' is specified, check if it exists, else raise an error
            if not self.session_store.has_session(command.session):
                raise ExecException(
                    f"VNC-Session not in Session-Store: {command.session}"
                )
            else:
                return self.session_store.get_client_by_session(command.session)

        # If neither 'creates_session' nor 'session' is provided
        default_session = 'default'

        if not self.session_store.has_session(default_session):
            # Create default session if it doesn't exist
            client = self.connect(command)
            self.session_store.set_session(default_session, client)
        else:
            # Retrieve the default session if it already exists
            client = self.session_store.get_client_by_session(default_session)

        return client

    def log_command(self, command: VncCommand):
        self.logger.info(f"Executing VNC-Command: '{command.cmd}'.")

    def send_keys(self, client, keys):
        for k in keys:
            client.keyPress(k)

    def _exec_cmd(self, command: VncCommand) -> Result:
        output = ''

        try:
            client = self.connect_use_session(command)
            if not (client and client.protocol.connected):
                return Result(output, 0)

            actions = {
                'key': lambda: client.keyPress(command.key),
                'type': lambda: self.send_keys(client, command.input),
                'move': lambda: client.mouseMove(command.x, command.y),
                'capture': lambda: client.captureScreen(command.filename),
                'click': lambda: client.mousePress(1),
                'rightclick': lambda: client.mousePress(3),
                'expectscreen': lambda: client.expectScreen(
                    command.filename, maxrms=command.maxrms
                ),
                'close': lambda: self.close_connection(getattr(command, 'session', 'default')),
            }
            action = actions.get(command.cmd)
            if action:
                action()

            else:
                raise ExecException(f"Unknown VNC command: {command.cmd}")

        except TimeoutError:
            self.cleanup()
            raise ExecException(
                f"VNC Timeout Error after {command.expect_timeout} seconds"
            )

        except (ValueError, AttributeError, AuthenticationError, OSError) as e:
            raise ExecException(f"VNC Execution Error: {e}")

        output = 'vnc_connected'
        return Result(output, 0)

    def close_connection(self, session_name: str = 'default'):
        """Closes the VNC connection for a given session."""
        if self.session_store.has_session(session_name):
            client = self.session_store.get_client_by_session(session_name)
            if client:
                try:
                    self.logger.info(
                        f"Closing VNC connection for session: {session_name}"
                    )
                    client.disconnect()
                    api.shutdown()
                    self.session_store.remove_session(session_name)
                    self.logger.info(
                        f"VNC session '{session_name}' closed and removed."
                    )
                except Exception as e:
                    self.logger.error(
                        f"Error closing VNC session '{session_name}': {str(e)}"
                    )
                    raise ExecException(f"Error closing VNC connection: {e}")
        else:
            self.logger.warning(
                f"VNC session '{session_name}' not found in session store."
            )

    def cleanup(self):
        self.session_store.clean_sessions()
        api.shutdown()
        self.logger.warning('VNC sessions cleaned up and VNC API shutdown.')
