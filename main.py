#!/usr/bin/env python3

import yaml
import schemas
import shellexecutor
import logging

logging.basicConfig(
                  filemode='w', level=logging.DEBUG)
logger = logging.getLogger("hackerman")

with open("example.yml") as f:
    config = yaml.safe_load(f)

pyconfig = schemas.Config.parse_obj(config)

se = shellexecutor.ShellExecutor(logger)

for command in pyconfig.commands:
    if command.type == "shell":
        se.exec(command)
