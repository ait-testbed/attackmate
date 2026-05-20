"""AttackMate reads a playbook and executes the attack chain.

A playbook is a structured sequence of commands, each dispatched to the
appropriate executor based on its type. Executors are instantiated lazily
on first use and cached for reuse. Available executors include
:class:`ShellExecutor`, :class:`SleepExecutor`, :class:`MsfModuleExecutor`,
and others registered via the executor factory.

This module exposes :class:`AttackMate`, which can be used standalone via
its :meth:`~AttackMate.main` entry point or embedded in a Python script
using :meth:`~AttackMate.run_command` for single-command execution.

.. seealso::
    :ref:`integration` for documentation on scripted usage.
"""

import time
from typing import Dict, Optional
import logging
from attackmate.result import Result
import attackmate.executors as executors
from attackmate.schemas.config import CommandConfig, Config, MsfConfig, SliverConfig
from attackmate.schemas.playbook import Playbook
from attackmate.schemas.command_types import Commands, Command
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.executors.executor_factory import executor_factory


class AttackMate:
    """Reads a playbook and executes the attack chain.

    Creates instances of all registered executors, iterates over the commands
    in the playbook, and dispatches each to the appropriate executor.

    Can be used standalone via :meth:`main`, or embedded in a Python script
    using :meth:`run_command` for single-command execution.

    :param playbook: The playbook to execute. Defaults to an empty playbook.
    :param config: AttackMate configuration. Defaults to a default :class:`Config`.
    :param varstore: Initial variables passed as a plain dictionary. If omitted,
        variables are read from the playbook's ``vars`` section.
    :param is_api_instance: Set to ``True`` when AttackMate is used as an embedded
        API rather than a standalone CLI process.

    Example::

        attackmate = AttackMate(config=config, varstore={"HOST": "10.0.0.1"})
        command = Command.create(type="shell", cmd="whoami")
        result = await attackmate.run_command(command)
    """

    def __init__(
        self,
        playbook: Optional[Playbook] = None,
        config: Optional[Config] = None,
        varstore: Optional[Dict] = None,
        is_api_instance: bool = False,
    ) -> None:
        """Constructor for AttackMate

        This constructor initializes the logger('playbook'), the playbook,
        the variable-parser and all the executors.

        Parameters
        ----------
        config_file : str
            The path to a yaml-playbook
        """
        self.logger = logging.getLogger('playbook')
        self.pm = ProcessManager()

        # Initialize playbook and config, with defaults if not provided
        self.playbook = playbook if playbook else self._default_playbook()
        self.pyconfig = config if config else self._default_config()

        self._initialize_variable_parser(varstore)
        self.msfsessionstore = executors.MsfSessionStore(self.varstore)
        self.executor_config = self._get_executor_config()
        self.executors: Dict[str, BaseExecutor] = {}
        self.is_api_instance = is_api_instance

    def _default_playbook(self) -> Playbook:
        return Playbook(commands=[], vars={})

    def _default_config(self) -> Config:
        return Config(
            cmd_config=CommandConfig(),
            msf_config=MsfConfig(),
            sliver_config=SliverConfig(),
            bettercap_config={},
            remote_config={}
        )

    def _initialize_variable_parser(self, varstore: Optional[Dict] = None):
        """Initializes the variable-parser

        The variablestore stores and replaces variables with values in certain strings
        """
        self.varstore = VariableStore()
        # if attackmate is imported and initialized in another project, vars can be passed as dict
        # otherwise variable store is initialized with vars from playbook
        self.varstore.from_dict(varstore if varstore else self.playbook.vars)
        self.varstore.replace_with_prefixed_env_vars()

    def _get_executor_config(self) -> dict:
        config = {
            'pm': self.pm,
            'varstore': self.varstore,
            'cmdconfig': self.pyconfig.cmd_config,
            'msfconfig': self.pyconfig.msf_config,
            'bettercap_config': self.pyconfig.bettercap_config,
            'remote_config': self.pyconfig.remote_config,
            'msfsessionstore': self.msfsessionstore,
            'sliver_config': self.pyconfig.sliver_config,
            'runfunc': self._run_commands,
        }
        return config

    def _get_executor(self, command_type: str) -> BaseExecutor:
        """Return the executor instance for the given command type.

        Executors are instantiated lazily on first use and cached for subsequent
        calls. If no executor for ``command_type`` exists yet, one is created via
        :func:`executor_factory.create_executor` and stored for reuse.

        :param command_type: The command type string (e.g. ``"shell"``, ``"ssh"``).
        :returns: The :class:`BaseExecutor` instance for that command type.
        """
        if command_type not in self.executors:
            self.executors[command_type] = executor_factory.create_executor(
                command_type, **self.executor_config
            )

        return self.executors[command_type]

    async def _run_commands(self, commands: Commands):
        """Execute a sequence of commands in order.

        Iterates over ``commands``, resolves the appropriate executor for each,
        and runs them sequentially. A configurable delay is applied before each
        command, except for ``sleep``, ``debug``, and ``setvar`` commands which
        are exempt from the delay.

        ``sftp`` commands are dispatched to the ``ssh`` executor.

        :param commands: A sequence of command instances to execute.

        .. note::
            The delay between commands is controlled by ``cmd_config.command_delay``
            in the :class:`Config`. Defaults to ``0`` if not set.
        """
        delay = self.pyconfig.cmd_config.command_delay or 0
        self.logger.info(f'Delay before commands: {delay} seconds')
        for command in commands:
            command_type = 'ssh' if command.type == 'sftp' else command.type
            executor = self._get_executor(command_type)
            if executor:
                if command.type not in ('sleep', 'debug', 'setvar'):
                    time.sleep(delay)
                await executor.run(command, is_api_instance=self.is_api_instance)

    async def run_command(self, command: Command) -> Result:
        """Execute a single command and return its result.

        Looks up the appropriate executor for the command type and runs it.
        One exception:``sftp`` commands are dispatched to the ``ssh`` executor.

        :param command: A command instance created via :meth:`Command.create`.
        :returns: A :class:`Result` object containing ``stdout`` and ``returncode``.
            Returns ``Result(None, None)`` if no executor is found.

        .. note::
            Commands running in backgound return
            ``Result('Command started in background', 0)`` immediately.
        """
        command_type = 'ssh' if command.type == 'sftp' else command.type
        executor = self._get_executor(command_type)
        if executor:
            result = await executor.run(command, self.is_api_instance)
        return result if result else Result(None, None)

    async def clean_session_stores(self):
        self.logger.warning('Cleaning up session stores')
        # msf
        if (msf_module_executor := self.executors.get('msf-module')):
            msf_module_executor.cleanup()
        if (msf_session_executor := self.executors.get('msf-session')):
            msf_session_executor.cleanup()
        # ssh
        if (ssh_executor := self.executors.get('ssh')):
            ssh_executor.cleanup()
        # vnc
        if (vnc_executor := self.executors.get('vnc')):
            vnc_executor.cleanup()
        # sliver
        if (sliver_executor := self.executors.get('sliver')):
            await sliver_executor.cleanup()
        # sliver
        if (sliver_session_executor := self.executors.get('sliver-session')):
            await sliver_session_executor.cleanup()
        if (remote_executor := self.executors.get('remote')):
            remote_executor.cleanup()

    async def main(self):
        """Execute the full playbook and clean up all sessions.

        Passes all commands from the playbook to :meth:`_run_commands`, then
        tears down open sessions and background processes. Handles
        :exc:`KeyboardInterrupt` gracefully.

        :returns: ``0`` on completion.
        """
        try:
            await self._run_commands(self.playbook.commands)
            await self.clean_session_stores()
            self.pm.kill_or_wait_processes()
        except KeyboardInterrupt:
            self.logger.warning('Program stopped manually')

        return 0
