#!/usr/bin/env python3

import sys
from .hackhelfer import HackHelfer

if __name__ == '__main__':
    hacky = HackHelfer("example.yml")
    sys.exit(hacky.main())
