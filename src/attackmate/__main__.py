#!/usr/bin/env python3
"""
__main__.py
=====================================
The main-file of AttackMate
"""
import sys
import argparse
from attackmate.attackmate import AttackMate
from attackmate.metadata import __version_string__
from attackmate.logging_setup import initialize_logger, initialize_output_logger, initialize_json_logger
from attackmate.playbook_parser import parse_playbook, parse_config


def parse_args():
    description = (
        'AttackMate is an attack orchestration tool' ' to execute full attack-chains based on playbooks.'
    )
    parser = argparse.ArgumentParser(prog='attackmate', description=description, epilog=__version_string__)
    parser.add_argument('--config', help='Configfile in yaml-format')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable verbose output')
    parser.add_argument('--json', action='store_true', default=False, help='log commands to attackmate.json')
    parser.add_argument('--version', action='version', version=__version_string__)
    parser.add_argument('playbook', help='Playbook in yaml-format')
    return parser.parse_args()


def main():
    args = parse_args()
    logger = initialize_logger(args.debug)
    initialize_output_logger(args.debug)
    initialize_json_logger(args.json)
    hacky = AttackMate(parse_playbook(args.playbook, logger), parse_config(args.config, logger))
    sys.exit(hacky.main())


if __name__ == '__main__':
    main()
