#!/usr/bin/env python3

import sys
import argparse
from .hackhelfer import HackHelfer


def parse_args():
    parser = argparse.ArgumentParser(
            prog='hackhelfer',
            description='Attack-Simulator for Testbeds')
    parser.add_argument(
            '--config',
            help='Attack-Playbook in yaml-format',
            required=True)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    hacky = HackHelfer(args.config)
    sys.exit(hacky.main())
