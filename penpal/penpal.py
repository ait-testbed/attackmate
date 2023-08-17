"""PenPal reads a playbook and executes the attack

A playbook stored in a dictionary with a list of attacks. Attacks
are executed by "Executors". There are many different
Executors like: ShellExecutor, SleepExecutor or MsfModuleExecutor
This class creates instances of all possible Executors, iterates
over all attacks and runs the specific Executor with the given
configuration.
"""

import yaml
import logging
from .shellexecutor import ShellExecutor
from .sleepexecutor import SleepExecutor
from .sshexecutor import SSHExecutor
from .msfexecutor import MsfModuleExecutor
from .msfsessionexecutor import MsfSessionExecutor
from .msfsessionstore import MsfSessionStore
from .sliverimplantexecutor import SliverImplantExecutor
from .debugexecutor import DebugExecutor
from .regexexecutor import RegExExecutor
from .schemas import Config
from .variablestore import VariableStore


class PenPal:
    def __init__(self, config_file: str) -> None:
        """ Constructor for PenPal

        This constructor initializes the logger('playbook'), the playbook,
        the variable-parser and all the executors.

        Parameters
        ----------
        config_file : str
            The path to a yaml-playbook
        """
        self.logger = logging.getLogger('playbook')
        self.pyconfig: Config
        self.parse_config(config_file)
        self.initialize_variable_parser()
        self.initialize_executors()

    def parse_config(self, config_file: str):
        """ Config-Parser for PenPal

        This parser reads the playbook-file and validates the config-settings.

        Parameters
        ----------
        config_file : str
            The path to a yaml-playbook

        Notes
        -----
        This method will exit(1) on errors.
        """
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
                self.pyconfig = Config.parse_obj(config)
        except OSError:
            self.logger.error(f"Could not open file: {config_file}")
            exit(1)
        except yaml.parser.ParserError as e:
            self.logger.error(e)
            exit(1)

    def initialize_variable_parser(self):
        """ Initializes the variable-parser

        The variablestore stores and replaces variables with values in certain strings
        """
        self.varstore = VariableStore()
        self.varstore.from_dict(self.pyconfig.vars)

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
        self.regex = RegExExecutor(self.varstore, self.pyconfig.cmd_config)
        self.sliverimplant = SliverImplantExecutor(self.pyconfig.cmd_config,
                                                   varstore=self.varstore,
                                                   sliver_config=self.pyconfig.sliver_config)

    def main(self):
        """ The main function

        This function calls the variable_parser() and interates
        over all configured commands and passes them to the
        executors.

        """
        for command in self.pyconfig.commands:
            if command.type == "shell":
                self.se.run(command)
            if command.type == "sleep":
                self.sleep.run(command)
            if command.type == "msf-module":
                self.msfmodule.run(command)
            if command.type == "msf-session":
                self.msfsession.run(command)
            if command.type == "ssh":
                self.ssh.run(command)
            if command.type == "debug":
                self.debugger.run(command)
            if command.type == "regex":
                self.regex.run(command)
            if command.type == "sliver-implant":
                self.sliverimplant.run(command)
