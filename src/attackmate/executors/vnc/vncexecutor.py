"""
vncexecutor.py
============================================
This class enables executing commands via vnc.
"""

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.schemas.vnc import VncCommand
from vncdotool import api
from vncdotool.client import AuthenticationError


class VncExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, cmdconfig=None, *, varstore: VariableStore):
        self.set_defaults()
        super().__init__(pm, varstore, cmdconfig)

    def set_defaults(self):
        self.hostname = None
        self.port = None
        self.display = None
        self.password = None
        self.client = None

    def connect(self, command: VncCommand) -> api.ThreadedVNCClientProxy:
        connection_string = self.hostname

        if self.display is not None:
            connection_string += f':{self.display}'
        if self.port is not None:
            if self.display is None:
                connection_string += f'::{self.port}'

        client = api.connect(connection_string, command.password)

        return client

    def cache_settings(self, command: VncCommand):
        if command.hostname:
            self.hostname = command.hostname
        if command.port:
            self.port = command.port
        if command.display:
            self.display = command.display
        if command.password:
            self.password = command.password

    def log_command(self, command: VncCommand):
        self.cache_settings(command)
        self.logger.info(f"Executing Vnc-Command: '{command.cmd}'. Host: {self.hostname}")

    def send_keys(self, client, keys):
        for k in keys:
            client.keyPress(k)

    def _exec_cmd(self, command: VncCommand) -> Result:
        self.cache_settings(command)

        try:
            if not self.client:
                self.client = self.connect(command)

            if command.cmd == 'key' and command.key:
                self.client.keyPress(command.key)
            elif command.cmd == 'type' and command.input:
                cl = self.client
                self.send_keys(cl, command.input)
            elif command.cmd == 'move':
                self.client.mouseMove(command.x, command.y)
            elif command.cmd == 'capture':
                self.client.captureScreen(command.filename)
            elif command.cmd == 'click':
                self.client.mousePress(1)
        except ValueError as e:
            raise ExecException(e)
        except AttributeError as e:
            raise ExecException(e)
        except AuthenticationError as e:
            raise ExecException(e)
        except OSError as e:
            raise ExecException(e)

        output = ''
        return Result(output, 0)
