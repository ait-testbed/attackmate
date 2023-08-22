"""
sliversessionexecutor.py
============================================
Execute Commands in a Sliver Session
"""

import asyncio
from sliver import SliverClientConfig, SliverClient
from sliver.session import InteractiveSession
# from sliver.protobuf import client_pb2
from .variablestore import VariableStore
from .baseexecutor import BaseExecutor, ExecException, Result
from .schemas import (BaseCommand, SliverSessionCDCommand,
                      SliverSessionLSCommand, SliverSessionNETSTATCommand,
                      SliverSessionSimpleCommand)
from datetime import datetime
from tabulate import tabulate


class SliverSessionExecutor(BaseExecutor):

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

    async def cd(self, command: SliverSessionCDCommand):
        self.logger.debug(f"{command.remote_path=}")
        session = await self.get_session_by_name(command.session)
        self.logger.debug(session)
        pwd = await session.cd(command.remote_path)
        self.logger.debug(pwd)
        self.result = Result(f"Path: {pwd.Path}", 0)

    async def ifconfig(self, command: SliverSessionSimpleCommand):
        session = await self.get_session_by_name(command.session)
        self.logger.debug(session)
        ifc = await session.ifconfig()
        self.logger.debug(ifc)
        lines = []
        for netif in ifc.NetInterfaces:
            ips = ""
            for ip in netif.IPAddresses:
                ips += ip
                ips += "\n"
            lines.append((netif.Index, ips, netif.MAC, netif.Name))
        output = "\n"
        output += tabulate(lines, headers=["Index", "IP Addresses", "MAC Address", "Interface"])
        output += "\n"
        self.result = Result(output, 0)

    async def ps(self, command: SliverSessionSimpleCommand):
        session = await self.get_session_by_name(command.session)
        self.logger.debug(session)
        processes = await session.ps()
        self.logger.debug(processes)
        lines = []
        for proc in processes:
            lines.append((proc.Pid, proc.Ppid, proc.Owner, proc.Architecture, proc.Executable))
        output = "\n"
        output += tabulate(lines, headers=["Pid", "Ppid", "Owner", "Arch", "Executable"])
        output += "\n"
        self.result = Result(output, 0)

    async def pwd(self, command: SliverSessionSimpleCommand):
        session = await self.get_session_by_name(command.session)
        self.logger.debug(session)
        pwd = await session.pwd()
        self.logger.debug(pwd)
        self.result = Result(f"Path: {pwd.Path}", 0)

    async def ls(self, command: SliverSessionLSCommand):
        self.logger.debug(f"{command.remote_path=}")
        session = await self.get_session_by_name(command.session)
        self.logger.debug(session)
        ls = await session.ls(command.remote_path)
        output = ""
        if ls:
            size = 0
            lines = []
            for f in ls.Files:
                size += f.Size
                isdir = ""
                if f.IsDir:
                    isdir = "<dir>"
                date_time = datetime.fromtimestamp(f.ModTime)
                lines.append((f.Mode, f.Name, isdir, date_time.ctime()))
            output = f"\n{ls.Path} ({len(ls.Files)} items, {size} bytes)\n"
            output += "\n"
            output += tabulate(lines)
            output += "\n"
            self.result = Result(output, 0)
        self.logger.debug(ls)

    async def netstat(self, command: SliverSessionNETSTATCommand):
        session = await self.get_session_by_name(command.session)
        self.logger.debug(session)
        net = await session.netstat(command.tcp, command.udp, command.ipv4, command.ipv6, command.listening)
        lines = []
        for entry in net.Entries:
            state = ""
            uid = ""
            if hasattr(entry, "SkState"):
                state = entry.SkState
            if hasattr(entry, "UID"):
                uid = entry.UID
            lines.append((entry.Protocol,
                          entry.LocalAddr.Ip + ":" + str(entry.LocalAddr.Port),
                          entry.RemoteAddr.Ip,
                          state,
                          str(entry.Process.Pid) + "/" + entry.Process.Executable,
                          uid))
        output = "\n"
        output += tabulate(lines, headers=["Protocol", "Local Address",
                                           "Foreign Address", "State",
                                           "PID/Program Name", "UID"])
        output += "\n"
        self.result = Result(output, 0)

    def log_command(self, command: BaseCommand):
        self.logger.info(f"Executing Sliver-Session-command: '{command.cmd}'")
        loop = asyncio.get_event_loop()
        coro = self.connect()
        loop.run_until_complete(coro)

    async def get_session_by_name(self, name) -> InteractiveSession:
        if self.client is None:
            raise ExecException("SliverClient is not defined")

        sessions = await self.client.sessions()
        for session in sessions:
            if session.Name == name and not session.IsDead:
                self.logger.debug(session)
                ret = await self.client.interact_session(session.ID)
                return ret

        raise ExecException("Active SliverSession not found")

    def _exec_cmd(self, command: BaseCommand) -> Result:
        loop = asyncio.get_event_loop()

        if command.cmd == "cd" and isinstance(command, SliverSessionCDCommand):
            coro = self.cd(command)
        elif command.cmd == "ls" and isinstance(command, SliverSessionLSCommand):
            coro = self.ls(command)
        elif command.cmd == "ifconfig" and isinstance(command, SliverSessionSimpleCommand):
            coro = self.ifconfig(command)
        elif command.cmd == "ps" and isinstance(command, SliverSessionSimpleCommand):
            coro = self.ps(command)
        elif command.cmd == "pwd" and isinstance(command, SliverSessionSimpleCommand):
            coro = self.pwd(command)
        elif command.cmd == "netstat" and isinstance(command, SliverSessionNETSTATCommand):
            coro = self.netstat(command)
        else:
            raise ExecException("Sliver Session Command unknown or faulty Command-config")
        loop.run_until_complete(coro)
        return self.result
