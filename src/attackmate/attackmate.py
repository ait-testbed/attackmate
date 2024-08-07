"""AttackMate reads a playbook and executes the attack

A playbook stored in a dictionary with a list of attacks. Attacks
are executed by "Executors". There are many different
Executors like: ShellExecutor, SleepExecutor or MsfModuleExecutor
This class creates instances of all possible Executors, iterates
over all attacks and runs the specific Executor with the given
configuration.
"""

from typing import Dict
import logging
import attackmate.executors as executors
from attackmate.schemas.config import Config
from attackmate.schemas.playbook import Playbook, Commands
from .variablestore import VariableStore
from .processmanager import ProcessManager
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.executors.executor_factory import executor_factory


class AttackMate:
    def __init__(self, playbook: Playbook, config: Config) -> None:
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
        self.pyconfig = config
        self.playbook = playbook
        self.initialize_variable_parser()
        self.msfsessionstore = executors.MsfSessionStore(self.varstore)
        self.executor_config = self.get_executor_config()
        self.executors: Dict[str, BaseExecutor] = {}

    def initialize_variable_parser(self):
        """Initializes the variable-parser

        The variablestore stores and replaces variables with values in certain strings
        """
        self.varstore = VariableStore()
        self.varstore.from_dict(self.playbook.vars)

    def get_executor_config(self) -> dict:
        config = {
            'pm': self.pm,
            'varstore': self.varstore,
            'cmdconfig': self.pyconfig.cmd_config,
            'msfconfig': self.pyconfig.msf_config,
            'msfsessionstore': self.msfsessionstore,
            'sliver_config': self.pyconfig.sliver_config,
        }
        return config

    def get_executor(self, command_type: str) -> BaseExecutor:
        if command_type not in self.executors:
            self.executors[command_type] = executor_factory.create_executor(
                command_type, **self.executor_config
            )

        return self.executors[command_type]

    def run_commands(self, commands: Commands):
        for command in commands:
            if command.type == 'sftp':
                executor = self.get_executor('ssh')
            else:
                executor = self.get_executor(command.type)
            if executor:
                executor.run(command)

    def main(self):
        """The main function

        Passes the main playbook-commands
        to run_commands

        """
        try:
            self.run_commands(self.playbook.commands)
            self.pm.kill_or_wait_processes()
        except KeyboardInterrupt:
            self.logger.warn('Program stopped manually')

        return 0
