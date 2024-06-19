#!/usr/bin/env python3
"""
__main__.py
=====================================
The main-file of AttackMate
"""

import os
import sys
import argparse
import yaml
import logging
from typing import Optional
from colorlog import ColoredFormatter
from .attackmate import AttackMate
from attackmate.schemas.config import Config
from attackmate.schemas.playbook import Playbook
from .metadata import __version_string__


def initialize_output_logger(debug: bool):
    output_logger = logging.getLogger('output')
    if debug:
        output_logger.setLevel(logging.DEBUG)
    else:
        output_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('output.log', mode='w')
    formatter = logging.Formatter(
            '--- %(asctime)s %(levelname)s: ---\n\n%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    output_logger.addHandler(file_handler)


def initialize_logger(debug: bool):
    playbook_logger = logging.getLogger('playbook')
    if debug:
        playbook_logger.setLevel(logging.DEBUG)
    else:
        playbook_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    LOGFORMAT = ('  %(asctime)s %(log_color)s%(levelname)-8s%(reset)s'
                 '| %(log_color)s%(message)s%(reset)s')
    formatter = ColoredFormatter(LOGFORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    playbook_logger.addHandler(console_handler)
    file_handler = logging.FileHandler('attackmate.log', mode='w')
    formatter = logging.Formatter(
            '%(asctime)s %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    playbook_logger.addHandler(file_handler)
    return playbook_logger


def load_configfile(config_file: str) -> Config:
    with open(config_file) as f:
        config = yaml.safe_load(f)
        return Config.model_validate(config)


def is_effectively_empty(file_path: str) -> bool:
    """strip the contents of the file from comments and whitespace to determine if it is truly empty"""
    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith('#'):
                return False
    return True


def parse_config(config_file: Optional[str], logger: logging.Logger) -> Config:
    """ Config-Parser for AttackMate

    This parser reads the configfile and validates the settings.
    If config_file is None, this function will try to load the
    config from ".attackmate.yml", "$HOME/.config/attackmate.yml" and
    "/etc/attackmate.yml". If no files are found or the files are empty,
    it uses default config variables.

    Parameters
    ----------
    config_file : str
        The path to a yaml-playbook

    Returns
    -------
    Config
        The parsed AttackMate config object

    """
    default_cfg_path = [
                        '.attackmate.yml',
                        os.environ['HOME'] + '/.config/attackmate.yml',
                        '/etc/attackmate.yml']
    try:
        if config_file is None:
            for file in default_cfg_path:
                cfg = None
                try:
                    if os.path.getsize(file) == 0 or is_effectively_empty(file):
                        continue
                    cfg = load_configfile(file)
                except OSError:
                    pass
                if cfg is not None:
                    logger.debug(f'Config file {file} loaded')
                    return cfg
            logger.debug('No config-file found or the default attackmate.yml was empty. Using default-config')
            return Config()
        else:
            if os.path.getsize(config_file) == 0 or is_effectively_empty(config_file):
                logger.debug(f'Config file {config_file} is empty. Using default config.')
                return Config()
            logger.debug(f'Config file {config_file} loaded')
            return load_configfile(config_file)
    except OSError:
        logger.error(f'Error: Could not open file {config_file}')
        exit(1)
    except yaml.parser.ParserError as e:
        logger.error(e)
        exit(1)


def parse_playbook(playbook_file: str, logger: logging.Logger) -> Playbook:
    """ Playbook-Parser for AttackMate

    This parser reads the playbook-file and validates the config-settings.

    Parameters
    ----------
    playbook_file : str
        The path to a yaml-playbook

    Returns
    -------
    Playbook
        The parsed AttackMate playbook object
    """
    try:
        with open(playbook_file) as f:
            pb_yaml = yaml.safe_load(f)
            playbook_object = Playbook.model_validate(pb_yaml)
            return playbook_object
    except OSError:
        logger.error(f'Error: Could not open playbook file {playbook_file}')
        exit(1)


def parse_args():
    description = 'AttackMate is an attack orchestration tool' \
                  ' to execute full attack-chains based on playbooks.'
    parser = argparse.ArgumentParser(
            prog='attackmate',
            description=description,
            epilog=__version_string__)
    parser.add_argument(
            '--config',
            help='Configfile in yaml-format')
    parser.add_argument(
            '--debug',
            action='store_true',
            default=False,
            help='Enable verbose output')
    parser.add_argument(
            '--version',
            action='version',
            version=__version_string__)
    parser.add_argument(
            'playbook',
            help='Playbook in yaml-format')
    return parser.parse_args()


def main():
    args = parse_args()
    logger = initialize_logger(args.debug)
    initialize_output_logger(args.debug)
    hacky = AttackMate(parse_playbook(args.playbook, logger), parse_config(args.config, logger))
    sys.exit(hacky.main())


if __name__ == '__main__':
    main()
