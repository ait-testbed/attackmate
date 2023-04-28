#!/usr/bin/env python3

import yaml
import schemas
import shellexecutor
import logging
from varparse import VarParse

logging.basicConfig(
                  filemode='w', level=logging.DEBUG)
logger = logging.getLogger("hackerman")

with open("example.yml") as f:
    config = yaml.safe_load(f)

pyconfig = schemas.Config.parse_obj(config)
print(pyconfig)

varparse = VarParse(pyconfig.vars)
se = shellexecutor.ShellExecutor(logger, pyconfig.cmd_config)

for command in pyconfig.commands:
    command.cmd = varparse.parse_command(command.cmd)
    if command.type == "shell":
        se.run(command)
