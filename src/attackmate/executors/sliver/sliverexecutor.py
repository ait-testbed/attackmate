"""
sliverexecutor.py
============================================
Execute Sliver Commands
"""

import asyncio
import os
import tempfile
from typing import Any
from sliver import SliverClientConfig, SliverClient
from sliver.protobuf import client_pb2
from attackmate.variablestore import VariableStore
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.sliver import SliverGenerateCommand, SliverHttpsListenerCommand
from attackmate.processmanager import ProcessManager


class SliverExecutor(BaseExecutor):

    def __init__(self, pm: ProcessManager, cmdconfig=None, *,
                 varstore: VariableStore,
                 sliver_config=None):
        self.sliver_config = sliver_config
        self.client = None
        self.tempfilestore: list[Any] = []
        self.client_config = None
        self.result = Result('', 1)

        if self.sliver_config.config_file:
            self.client_config = SliverClientConfig.parse_config_file(sliver_config.config_file)
            self.client = SliverClient(self.client_config)
        super().__init__(pm, varstore, cmdconfig)

    async def connect(self) -> None:
        if self.client:
            await self.client.connect()
            version = await self.client.version()
            self.logger.debug(version)

    async def start_https_listener(self, command: SliverHttpsListenerCommand):
        self.logger.debug(f'{command.host=}')
        if self.client is None:
            raise ExecException('SliverClient is not defined')
        listener = await self.client.start_https_listener(command.host,
                                                          CmdVars.variable_to_int('port', command.port),
                                                          command.website,
                                                          command.domain,
                                                          b'',
                                                          b'',
                                                          command.acme,
                                                          command.persistent,
                                                          command.enforce_otp,
                                                          command.randomize_jarm,
                                                          CmdVars.variable_to_int('long_poll_timeout',
                                                                                  command.long_poll_timeout),
                                                          CmdVars.variable_to_int('long_poll_jitter',
                                                                                  command.long_poll_jitter),
                                                          CmdVars.variable_to_int('timeout', command.timeout))
        self.result = Result(f'JobID: {listener.JobID}', 0)

    def prepare_implant_config(self, command: SliverGenerateCommand) -> client_pb2.ImplantConfig:
        c2 = client_pb2.ImplantC2()
        c2.URL = command.c2url
        c2.Priority = 0
        outformat = client_pb2.OutputFormat.EXECUTABLE
        implconfig = client_pb2.ImplantConfig()
        implconfig.IsService = False
        implconfig.IsSharedLib = False
        implconfig.IsShellcode = False

        if command.format == 'SERVICE':
            outformat = client_pb2.OutputFormat.SERVICE
            implconfig.IsService = True

        if command.format == 'SHARED_LIB':
            outformat = client_pb2.OutputFormat.SHARED_LIB
            implconfig.IsSharedLib = True

        if command.format == 'SHELLCODE':
            outformat = client_pb2.OutputFormat.SHELLCODE
            implconfig.IsShellcode = True

        implconfig.C2.extend([c2])
        implconfig.IsBeacon = command.IsBeacon
        if command.IsBeacon:
            implconfig.BeaconInterval = CmdVars.variable_to_int('BeaconInterval',
                                                                command.BeaconInterval)
        implconfig.RunAtLoad = command.RunAtLoad
        implconfig.Evasion = command.Evasion
        target = command.target.split('/')
        implconfig.GOOS = target[0]
        implconfig.GOARCH = target[1]
        implconfig.Name = command.name
        implconfig.Format = outformat
        implconfig.FileName = 'linux_implant'
        return implconfig

    def save_implant(self, implant: client_pb2.Generate) -> str:
        if hasattr(implant, 'filepath'):
            implant_path = implant.filepath
        else:
            tmpfile = tempfile.NamedTemporaryFile()
            self.tempfilestore.append(tmpfile)
            implant_path = tmpfile.name

        if os.path.exists(implant_path):
            os.remove(implant_path)

        with open(implant_path, 'wb') as new_file:
            new_file.write(implant.File.Data)

        self.varstore.set_variable('LAST_SLIVER_IMPLANT', implant_path)

        return implant_path

    async def generate_implant(self, command: SliverGenerateCommand):
        implconfig = self.prepare_implant_config(command)

        if self.client is None:
            raise ExecException('SliverClient is not defined')

        builds = await self.client.implant_builds()
        if command.name in builds.keys():
            self.logger.debug('Implant found. Delete it')
            await self.client.delete_implant_build(command.name)

        implant = await self.client.generate_implant(implconfig)
        length = len(implant.File.Data)
        self.result.stdout = f'Created Sliver-Implant: {implant.File.Name}. with {length} bytes'
        implant_path = self.save_implant(implant)
        self.logger.debug(f'Saved {implant.File.Name} to {implant_path}')
        self.result.returncode = 0

    def log_command(self, command: BaseCommand):
        self.logger.info(f"Executing Sliver-command: '{command.cmd}'")
        loop = asyncio.get_event_loop()
        coro = self.connect()
        loop.run_until_complete(coro)

    def _exec_cmd(self, command: BaseCommand) -> Result:
        loop = asyncio.get_event_loop()

        if command.cmd == 'start_https_listener' and isinstance(command, SliverHttpsListenerCommand):
            coro = self.start_https_listener(command)
        elif command.cmd == 'generate_implant' and isinstance(command, SliverGenerateCommand):
            coro = self.generate_implant(command)
        else:
            raise ExecException('Sliver Command unknown or faulty Command-config')
        try:
            loop.run_until_complete(coro)
        except Exception as e:
            raise ExecException(e)
        return self.result
