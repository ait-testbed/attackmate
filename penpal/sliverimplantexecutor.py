"""
sliverimplantexecutor.py
============================================
Generate Sliver Implants
"""

import asyncio
from sliver import SliverClientConfig, SliverClient
from .variablestore import VariableStore
from .baseexecutor import BaseExecutor, Result
from .schemas import SliverImplantCommand


class SliverImplantExecutor(BaseExecutor):

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

    def log_command(self, command: SliverImplantCommand):
        self.logger.info(f"Generating Sliver-Implant: '{command.name}'")
        loop = asyncio.get_event_loop()
        coro = self.connect()
        loop.run_until_complete(coro)

    async def run_command(self):
        self.result.stdout = await self.client.version()
        self.result.returncode = 0

    def _exec_cmd(self, command: SliverImplantCommand) -> Result:
        loop = asyncio.get_event_loop()
        coro = self.run_command()
        loop.run_until_complete(coro)
        return self.result
