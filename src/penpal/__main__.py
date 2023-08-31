#!/usr/bin/env python3
"""
__main__.py
=====================================
The main-file of PenPal
"""

import os
import sys
import argparse
import yaml
import logging
from typing import Optional
from colorlog import ColoredFormatter
from .penpal import PenPal
from .schemas import Config, Playbook
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
    return playbook_logger


def load_configfile(config_file: str) -> Config:
    with open(config_file) as f:
        config = yaml.safe_load(f)
        return Config.parse_obj(config)


def parse_config(config_file: Optional[str], logger: logging.Logger) -> Config:
    """ Config-Parser for PenPal

    This parser reads the configfile and validates the settings.
    If config_file is None, this function will try to load the
    config from ".penpal.yml", "$HOME/.config/penpal.yml" and
    "/etc/penpal.yml"

    Parameters
    ----------
    config_file : str
        The path to a yaml-playbook

    Returns
    -------
    Config
        The parsed PenPal config object

    """
    default_cfg_path = [
                        ".penpal.yml",
                        os.environ['HOME'] + "/.config/penpal.yml",
                        "/etc/penpal.yml"]
    try:
        if config_file is None:
            for file in default_cfg_path:
                cfg = None
                try:
                    cfg = load_configfile(file)
                except OSError:
                    pass
                if cfg is not None:
                    logger.debug(f"Cfgfile {file} loaded")
                    return cfg
            logger.debug("No config-file found. Using empty default-config")
            return Config()
        else:
            logger.debug(f"Cfgfile {config_file} loaded")
            return load_configfile(config_file)
    except OSError:
        logger.error(f"Error: Could not open file {config_file}")
        exit(1)
    except yaml.parser.ParserError as e:
        logger.error(e)
        exit(1)


def parse_playbook(playbook_file: str, logger: logging.Logger) -> Playbook:
    """ Playbook-Parser for PenPal

    This parser reads the playbook-file and validates the config-settings.

    Parameters
    ----------
    playbook_file : str
        The path to a yaml-playbook

    Returns
    -------
    Playbook
        The parsed PenPal playbook object
    """
    try:
        with open(playbook_file) as f:
            pb_yaml = yaml.safe_load(f)
            playbook_object = Playbook.parse_obj(pb_yaml)
            return playbook_object
    except OSError:
        logger.error(f"Error: Could not open playbook file {playbook_file}")
        exit(1)


def parse_args():
    description = 'PenPal is an attack orchestration tool' \
                  'that executes full attack-chains based on playbooks.'
    parser = argparse.ArgumentParser(
            prog='penpal',
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
            help="Playbook in yaml-format")
    return parser.parse_args()


def main():
    args = parse_args()
    logger = initialize_logger(args.debug)
    initialize_output_logger(args.debug)
    hacky = PenPal(parse_playbook(args.playbook, logger), parse_config(args.config, logger))
    sys.exit(hacky.main())


if __name__ == '__main__':
    main()
