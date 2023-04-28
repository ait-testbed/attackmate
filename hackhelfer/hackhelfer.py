#!/usr/bin/env python3

import yaml
import logging
from .shellexecutor import ShellExecutor
from .schemas import Config
from .varparse import VarParse


class HackHelfer:
    def __init__(self, config_file) -> None:
        self.logger = logging.getLogger('playbook')
        self.pyconfig = None
        self.parse_config(config_file)
        self.initialize_variable_parser()
        self.initialize_executors()

    def parse_config(self, config_file):
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
        except OSError:
            self.logger.error(f"Could not open file: {config_file}")
            exit(1)

        self.pyconfig = Config.parse_obj(config)

    def initialize_variable_parser(self):
        self.varparse = VarParse(self.pyconfig.vars)

    def initialize_executors(self):
        self.se = ShellExecutor(self.pyconfig.cmd_config)

    def main(self):
        self.initialize_variable_parser()
        for command in self.pyconfig.commands:
            command.cmd = self.varparse.parse_command(command.cmd)
            if command.type == "shell":
                self.se.run(command)
