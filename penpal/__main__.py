#!/usr/bin/env python3
"""
__main__.py
=====================================
The main-file of PenPal
"""

import sys
import argparse
import logging
from colorlog import ColoredFormatter
from .penpal import PenPal
from .metadata import __version_string__


def initialize_output_logger(debug: bool):
    output_logger = logging.getLogger('output')
    if debug:
        output_logger.setLevel(logging.DEBUG)
    else:
        output_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("output.log", mode='w')
    formatter = logging.Formatter(
            '--- %(asctime)s %(levelname)s: ---\n\n%(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    output_logger.addHandler(file_handler)


def initialize_logger(debug: bool):
    playbook_logger = logging.getLogger('playbook')
    if debug:
        playbook_logger.setLevel(logging.DEBUG)
    else:
        playbook_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    LOGFORMAT = ("  %(asctime)s %(log_color)s%(levelname)-8s%(reset)s"
                 "| %(log_color)s%(message)s%(reset)s")
    formatter = ColoredFormatter(LOGFORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)
    playbook_logger.addHandler(console_handler)
    file_handler = logging.FileHandler("penpal.log", mode='w')
    formatter = logging.Formatter(
            '%(asctime)s %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    playbook_logger.addHandler(file_handler)


def parse_args():
    description = 'PenPal is an attack orchestration tool' \
                  'that executes full attack-chains based on playbooks.'
    parser = argparse.ArgumentParser(
            prog='penpal',
            description=description,
            epilog=__version_string__)
    parser.add_argument(
            '--config',
            help='Attack-Playbook in yaml-format',
            required=True)
    parser.add_argument(
            '--debug',
            action='store_true',
            default=False,
            help='Enable verbose output')
    parser.add_argument(
            '--version',
            action='version',
            version=__version_string__)
    return parser.parse_args()


def main():
    args = parse_args()
    initialize_logger(args.debug)
    initialize_output_logger(args.debug)
    hacky = PenPal(args.config)
    sys.exit(hacky.main())


if __name__ == '__main__':
    main()
