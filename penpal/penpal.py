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
from .msfexecutor import MsfModuleExecutor, MsfSessionExecutor
from .msfsessionstore import MsfSessionStore
from .schemas import Config
from .varparse import VarParse


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
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
                self.pyconfig = Config.parse_obj(config)
        except OSError:
            self.logger.error(f"Could not open file: {config_file}")
            exit(1)

    def initialize_variable_parser(self):
        self.varparse = VarParse(self.pyconfig.vars)

    def initialize_executors(self):
        self.msfsessionstore = MsfSessionStore()
        self.se = ShellExecutor(self.pyconfig.cmd_config)
        self.sleep = SleepExecutor(self.pyconfig.cmd_config)
        self.msfmodule = MsfModuleExecutor(self.pyconfig.cmd_config,
                                           msfconfig=self.pyconfig.msf_config,
                                           msfsessionstore=self.msfsessionstore)
        self.msfsession = MsfSessionExecutor(
                self.pyconfig.cmd_config,
                msfconfig=self.pyconfig.msf_config,
                msfsessionstore=self.msfsessionstore)

    def main(self):
        self.initialize_variable_parser()
        for command in self.pyconfig.commands:
            command.cmd = self.varparse.parse_command(command.cmd)
            if command.type == "shell":
                self.se.run(command)
            if command.type == "sleep":
                self.sleep.run(command)
            if command.type == "msf-module":
                self.msfmodule.run(command)
            if command.type == "msf-session":
                self.msfsession.run(command)
