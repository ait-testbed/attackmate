import os
import logging
import traceback
import yaml
from typing import Optional
from pathlib import Path
from pydantic import ValidationError
from attackmate.schemas.playbook import Playbook
from attackmate.schemas.config import Config


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
    """Config-Parser for AttackMate

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
        '/etc/attackmate.yml',
    ]
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
    """Playbook-Parser for AttackMate

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

    # Get the path of the current working directory
    current_working_directory = Path.cwd()

    # Construct the path to the default playbooks directory
    default_playbook_location = Path('/etc/attackmate/playbooks')

    playbook_file_path = Path(playbook_file)
    target_file = None

    try:
        # 1 # Check provided path
        if playbook_file_path.exists():
            target_file = playbook_file_path

        # 2 # Check current working directory
        elif (current_working_directory / playbook_file_path).exists():
            target_file = current_working_directory / playbook_file_path

        # 3 # Check default playbook directory
        elif (default_playbook_location / playbook_file_path).exists():
            target_file = default_playbook_location / playbook_file_path
        else:
            logger.error(
                "Error: Playbook file not found under '/non/existent/path/playbook.yml'"
                + ' or in the current directory or in /etc/attackmate/playbooks'
            )
            exit(1)

    finally:
        if target_file:
            logger.debug(f'Playbook target filepath is set to: {target_file}')
        else:
            logger.debug('Playbook target filepath is not set')

    try:
        with open(target_file) as f:
            playbook_yaml = yaml.safe_load(f)
            playbook_object = Playbook.model_validate(playbook_yaml)
            return playbook_object
    except OSError:
        logger.error(f'Error: Could not open playbook file {target_file}')
        exit(1)
    except ValidationError as e:
        logger.error(f'A Validation error occured when parsing playbook file {playbook_file}')
        for error in e.errors():
            if error['type'] == 'missing':
                logger.error(
                    f'Missing field in {error["loc"][-2]} command: {error["loc"][-1]} - {error["msg"]}'
                )
            elif error['type'] == 'literal_error':
                logger.error(
                    f'Invalid value in {error["loc"][-2]} command: {error["loc"][-1]} - {error["msg"]}'
                )
            elif error['type'] == 'value_error':
                logger.error(
                    f'Value error in command {int(error["loc"][-2]) + 1}: '
                    f'{error["loc"][-1]} - {error["msg"]}'
                )
        logger.error(traceback.format_exc())
        exit(1)
