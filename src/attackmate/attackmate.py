"""AttackMate reads a playbook and executes the attack

A playbook stored in a dictionary with a list of attacks. Attacks
are executed by "Executors". There are many different
Executors like: ShellExecutor, SleepExecutor or MsfModuleExecutor
This class creates instances of all possible Executors, iterates
over all attacks and runs the specific Executor with the given
configuration.
"""

import logging
from attackmate.executors import (
    ShellExecutor,
    SSHExecutor,
    MsfSessionExecutor,
    MsfPayloadExecutor,
    MsfSessionStore,
    MsfModuleExecutor,
    SliverExecutor,
    SliverSessionExecutor,
    FatherExecutor,
    WebServExecutor,
    HttpClientExecutor,
    SetVarExecutor,
    SleepExecutor,
    TempfileExecutor,
    DebugExecutor,
    IncludeExecutor,
    RegExExecutor,
)
from attackmate.schemas.config import Config
from attackmate.schemas.playbook import Playbook, Commands
from .variablestore import VariableStore
from .processmanager import ProcessManager


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
        self.initialize_executors()

    def initialize_variable_parser(self):
        """Initializes the variable-parser

        The variablestore stores and replaces variables with values in certain strings
        """
        self.varstore = VariableStore()
        self.varstore.from_dict(self.playbook.vars)

    def initialize_executors(self):
        """Initialize all Executors

        Executors are supposed to execute commands. This method initializes
        all possible executors.

        """
        self.msfsessionstore = MsfSessionStore(self.varstore)
        executor_classes = {
            'shell': ShellExecutor,
            'sleep': SleepExecutor,
            'ssh': SSHExecutor,
            'father': FatherExecutor,
            'msf-module': MsfModuleExecutor,
            'msf-payload': MsfPayloadExecutor,
            'msf-session': MsfSessionExecutor,
            'debug': DebugExecutor,
            'webserv': WebServExecutor,
            'setvar': SetVarExecutor,
            'regex': RegExExecutor,
            'sliver': SliverExecutor,
            'sliver-session': SliverSessionExecutor,
            'mktemp': TempfileExecutor,
            'include': IncludeExecutor,
            'http-client': HttpClientExecutor,
        }
        self.executors = {
            key: cls(
                self.pm,
                self.pyconfig.cmd_config,
                varstore=self.varstore,
                msfconfig=self.pyconfig.msf_config if 'msf' in key else None,
                msfsessionstore=self.msfsessionstore if key == 'msf-session' else None,
                sliver_config=self.pyconfig.sliver_config if 'sliver' in key else None,
                runfunc=self.run_commands if key == 'include' else None,
            )
            for key, cls in executor_classes.items()
        }

    def run_commands(self, commands: Commands):
        """Pass commands to the executors

        This function interates over all configured
        commands and passes them to the executors.

        """
        for command in commands:
            executor = self.executors.get(command.type)
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
