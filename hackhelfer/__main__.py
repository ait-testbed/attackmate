#!/usr/bin/env python3

import sys
import argparse
import logging
from colorlog import ColoredFormatter
from .hackhelfer import HackHelfer


def initialize_output_logger():
    output_logger = logging.getLogger('output')
    output_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("output.log", mode='w')
    formatter = logging.Formatter(
            '--- %(asctime)s %(levelname)s: ---\n\n%(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    output_logger.addHandler(file_handler)


def initialize_logger():
    playbook_logger = logging.getLogger('playbook')
    playbook_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    LOGFORMAT = """  %(asctime)s %(log_color)s%(levelname)-8s%(reset)s
    | %(log_color)s%(message)s%(reset)s"""
    formatter = ColoredFormatter(LOGFORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)
    playbook_logger.addHandler(console_handler)
    file_handler = logging.FileHandler("hackhelfer.log", mode='w')
    formatter = logging.Formatter(
            '%(asctime)s %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    playbook_logger.addHandler(file_handler)
    return playbook_logger


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
    logger = initialize_logger()
    logger = initialize_output_logger()
    hacky = HackHelfer(args.config, logger)
    sys.exit(hacky.main())
