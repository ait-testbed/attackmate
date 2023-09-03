"""AttackMate reads a playbook and executes the attack

A playbook stored in a dictionary with a list of attacks. Attacks
are executed by "Executors". There are many different
Executors like: ShellExecutor, SleepExecutor or MsfModuleExecutor
This class creates instances of all possible Executors, iterates
over all attacks and runs the specific Executor with the given
configuration.
"""

import logging
from .shellexecutor import ShellExecutor
from .sleepexecutor import SleepExecutor
from .sshexecutor import SSHExecutor
from .msfexecutor import MsfModuleExecutor
from .msfsessionexecutor import MsfSessionExecutor
from .msfsessionstore import MsfSessionStore
from .sliverexecutor import SliverExecutor
from .fatherexecutor import FatherExecutor
from .sliversessionexecutor import SliverSessionExecutor
from .tempfileexecutor import TempfileExecutor
from .debugexecutor import DebugExecutor
from .regexexecutor import RegExExecutor
from .schemas import Config, Playbook
from .variablestore import VariableStore


class AttackMate:
    def __init__(self, playbook: Playbook, config: Config) -> None:
        """ Constructor for AttackMate

        This constructor initializes the logger('playbook'), the playbook,
        the variable-parser and all the executors.

        Parameters
        ----------
        config_file : str
            The path to a yaml-playbook
        """
        self.logger = logging.getLogger('playbook')
        self.pyconfig = config
        self.playbook = playbook
        self.initialize_variable_parser()
        self.initialize_executors()

    def initialize_variable_parser(self):
        """ Initializes the variable-parser

        The variablestore stores and replaces variables with values in certain strings
        """
        self.varstore = VariableStore()
        self.varstore.from_dict(self.playbook.vars)

    def initialize_executors(self):
        """ Initialize all Executors

        Executors are supposed to execute commands. This method initializes
        all possible executors.

        """
        self.msfsessionstore = MsfSessionStore(self.varstore)
        self.se = ShellExecutor(self.varstore, self.pyconfig.cmd_config)
        self.sleep = SleepExecutor(self.pyconfig.cmd_config,
                                   varstore=self.varstore)
        self.ssh = SSHExecutor(self.pyconfig.cmd_config,
                               varstore=self.varstore)
        self.father = FatherExecutor(self.varstore, self.pyconfig.cmd_config)
        self.msfmodule = MsfModuleExecutor(self.pyconfig.cmd_config,
                                           varstore=self.varstore,
                                           msfconfig=self.pyconfig.msf_config,
                                           msfsessionstore=self.msfsessionstore)
        self.msfsession = MsfSessionExecutor(
                self.pyconfig.cmd_config,
                varstore=self.varstore,
                msfconfig=self.pyconfig.msf_config,
                msfsessionstore=self.msfsessionstore)
        self.debugger = DebugExecutor(self.varstore, self.pyconfig.cmd_config)
        self.mktemp = TempfileExecutor(self.varstore, self.pyconfig.cmd_config)
        self.regex = RegExExecutor(self.varstore, self.pyconfig.cmd_config)
        self.sliver = SliverExecutor(self.pyconfig.cmd_config,
                                     varstore=self.varstore,
                                     sliver_config=self.pyconfig.sliver_config)
        self.sliversession = SliverSessionExecutor(self.pyconfig.cmd_config,
                                                   varstore=self.varstore,
                                                   sliver_config=self.pyconfig.sliver_config)

    def main(self):
        """ The main function

        This function interates over all configured
        commands and passes them to the executors.

        """
        for command in self.playbook.commands:
            if command.type == "shell":
                self.se.run(command)
            if command.type == "father":
                self.father.run(command)
            if command.type == "sleep":
                self.sleep.run(command)
            if command.type == "msf-module":
                self.msfmodule.run(command)
            if command.type == "msf-session":
                self.msfsession.run(command)
            if command.type in ["ssh", "sftp"]:
                self.ssh.run(command)
            if command.type == "debug":
                self.debugger.run(command)
            if command.type == "regex":
                self.regex.run(command)
            if command.type == "sliver":
                self.sliver.run(command)
            if command.type == "sliver-session":
                self.sliversession.run(command)
            if command.type == "mktemp":
                self.mktemp.run(command)
