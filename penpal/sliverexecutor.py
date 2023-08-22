"""
sliverexecutor.py
============================================
Execute Sliver Commands
"""

import asyncio
from sliver import SliverClientConfig, SliverClient
# from sliver.protobuf import client_pb2
from .variablestore import VariableStore
from .baseexecutor import BaseExecutor, Result
from .schemas import BaseCommand, SliverHttpsListenerCommand


class SliverExecutor(BaseExecutor):

    def __init__(self, cmdconfig=None, *,
                 varstore: VariableStore,
                 sliver_config=None):
        self.sliver_config = sliver_config
        self.client = None
        self.client_config = None
        self.result = Result("", 1)

        if self.sliver_config.config_file:
            self.client_config = SliverClientConfig.parse_config_file(sliver_config.config_file)
            self.client = SliverClient(self.client_config)
        super().__init__(varstore, cmdconfig)

    async def connect(self) -> None:
        if self.client:
            await self.client.connect()
            version = await self.client.version()
            self.logger.debug(version)

    async def start_https_listener(self, command: SliverHttpsListenerCommand):
        self.logger.debug(f"{command.host=}")

    def log_command(self, command: BaseCommand):
        self.logger.info(f"Executing Sliver-command: '{command.cmd}'")
        loop = asyncio.get_event_loop()
        coro = self.connect()
        loop.run_until_complete(coro)

    def _exec_cmd(self, command: BaseCommand) -> Result:
        loop = asyncio.get_event_loop()
        if command == "start_https_listener" and isinstance(command, SliverHttpsListenerCommand):
            coro = self.start_https_listener(command)
        loop.run_until_complete(coro)
        return self.result
