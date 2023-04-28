#!/usr/bin/env python3

import yaml
import logging
from .shellexecutor import ShellExecutor
from .schemas import Config
from .varparse import VarParse


class HackHelfer:
    def __init__(self, config_file) -> None:
        logging.basicConfig(
                          filemode='w', level=logging.DEBUG)
        self.logger = logging.getLogger("hackerman")
        self.pyconfig = None
        self.parse_config(config_file)
        self.initialize_variable_parser()
        self.initialize_executors()

    def parse_config(self, config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)

        self.pyconfig = Config.parse_obj(config)

    def initialize_variable_parser(self):
        self.varparse = VarParse(self.pyconfig.vars)

    def initialize_executors(self):
        self.se = ShellExecutor(self.logger, self.pyconfig.cmd_config)

    def main(self):
        self.initialize_variable_parser()
        for command in self.pyconfig.commands:
            command.cmd = self.varparse.parse_command(command.cmd)
            if command.type == "shell":
                self.se.run(command)
