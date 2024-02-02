"""AttackMate reads a playbook and executes the attack

A playbook stored in a dictionary with a list of attacks. Attacks
are executed by "Executors". There are many different
Executors like: ShellExecutor, SleepExecutor or MsfModuleExecutor
This class creates instances of all possible Executors, iterates
over all attacks and runs the specific Executor with the given
configuration.
"""

import logging
from attackmate.executors.shell.shellexecutor import ShellExecutor
from attackmate.executors.ssh.sshexecutor import SSHExecutor
from attackmate.executors.metasploit.msfsessionexecutor import MsfSessionExecutor
from attackmate.executors.metasploit.msfpayloadexecutor import MsfPayloadExecutor
from attackmate.executors.metasploit.msfsessionstore import MsfSessionStore
from attackmate.executors.metasploit.msfexecutor import MsfModuleExecutor
from attackmate.executors.sliver.sliverexecutor import SliverExecutor
from attackmate.executors.sliver.sliversessionexecutor import SliverSessionExecutor
from attackmate.executors.father.fatherexecutor import FatherExecutor
from attackmate.executors.http.webservexecutor import WebServExecutor
from attackmate.executors.http.httpclientexecutor import HttpClientExecutor
from attackmate.executors.common.setvarexecutor import SetVarExecutor
from attackmate.executors.common.sleepexecutor import SleepExecutor
from attackmate.executors.common.tempfileexecutor import TempfileExecutor
from attackmate.executors.common.debugexecutor import DebugExecutor
from attackmate.executors.common.includeexecutor import IncludeExecutor
from attackmate.executors.common.regexexecutor import RegExExecutor
from attackmate.schemas.config import Config
from attackmate.schemas.playbook import Playbook, Commands
from .variablestore import VariableStore
from .processmanager import ProcessManager


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
        self.pm = ProcessManager()
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
        self.se = ShellExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.sleep = SleepExecutor(self.pm, self.pyconfig.cmd_config,
                                   varstore=self.varstore)
        self.ssh = SSHExecutor(self.pm, self.pyconfig.cmd_config,
                               varstore=self.varstore)
        self.father = FatherExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.msfmodule = MsfModuleExecutor(self.pm, self.pyconfig.cmd_config,
                                           varstore=self.varstore,
                                           msfconfig=self.pyconfig.msf_config,
                                           msfsessionstore=self.msfsessionstore)
        self.msfpayload = MsfPayloadExecutor(self.pm, self.varstore,
                                             self.pyconfig.cmd_config,
                                             msfconfig=self.pyconfig.msf_config)
        self.msfsession = MsfSessionExecutor(
                self.pm,
                self.pyconfig.cmd_config,
                varstore=self.varstore,
                msfconfig=self.pyconfig.msf_config,
                msfsessionstore=self.msfsessionstore)
        self.debugger = DebugExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.webserv = WebServExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.setvar = SetVarExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.mktemp = TempfileExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.regex = RegExExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.httpclient = HttpClientExecutor(self.pm, self.varstore, self.pyconfig.cmd_config)
        self.include = IncludeExecutor(self.pm, self.pyconfig.cmd_config,
                                       varstore=self.varstore,
                                       runfunc=self.run_commands)
        self.sliver = SliverExecutor(self.pm, self.pyconfig.cmd_config,
                                     varstore=self.varstore,
                                     sliver_config=self.pyconfig.sliver_config)
        self.sliversession = SliverSessionExecutor(self.pm, self.pyconfig.cmd_config,
                                                   varstore=self.varstore,
                                                   sliver_config=self.pyconfig.sliver_config)

    def run_commands(self, commands: Commands):
        """ Pass commands to the executors

        This function interates over all configured
        commands and passes them to the executors.

        """
        for command in commands:
            if command.type == 'shell':
                self.se.run(command)
            if command.type == 'father':
                self.father.run(command)
            if command.type == 'sleep':
                self.sleep.run(command)
            if command.type == 'msf-module':
                self.msfmodule.run(command)
            if command.type == 'msf-session':
                self.msfsession.run(command)
            if command.type == 'msf-payload':
                self.msfpayload.run(command)
            if command.type in ['ssh', 'sftp']:
                self.ssh.run(command)
            if command.type == 'debug':
                self.debugger.run(command)
            if command.type == 'setvar':
                self.setvar.run(command)
            if command.type == 'regex':
                self.regex.run(command)
            if command.type == 'sliver':
                self.sliver.run(command)
            if command.type == 'sliver-session':
                self.sliversession.run(command)
            if command.type == 'mktemp':
                self.mktemp.run(command)
            if command.type == 'include':
                self.include.run(command)
            if command.type == 'webserv':
                self.webserv.run(command)
            if command.type == 'http-client':
                self.httpclient.run(command)

    def main(self):
        """ The main function

            Passes the main playbook-commands
            to run_commands

        """
        try:
            self.run_commands(self.playbook.commands)
            self.pm.kill_or_wait_processes()
        except KeyboardInterrupt:
            self.logger.warn('Program stopped manually')

        return 0
