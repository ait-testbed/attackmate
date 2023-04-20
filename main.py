#!/usr/bin/env python3

import yaml
import schemas


with open("example.yml") as f:
    config = yaml.safe_load(f)

pyconfig = schemas.Config.parse_obj(config)

print(pyconfig)
