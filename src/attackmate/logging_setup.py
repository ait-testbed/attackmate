# logging_setup.py

import logging
import sys
from colorlog import ColoredFormatter

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
OUTPUT_LOG_FILE = 'output.log'
PLAYBOOK_LOG_FILE = 'attackmate.log'
JSON_LOG_FILE = 'attackmate.json'

PLAYBOOK_CONSOLE_FORMAT = '  %(asctime)s %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'
DEFAULT_FILE_FORMAT = '%(asctime)s %(levelname)s - %(message)s'
OUTPUT_FILE_FORMAT = '--- %(asctime)s %(levelname)s: ---\n\n%(message)s'


def initialize_output_logger(debug: bool, append_logs: bool):
    output_logger = logging.getLogger('output')
    output_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    formatter = logging.Formatter(OUTPUT_FILE_FORMAT, datefmt=DATE_FORMAT)
    file_handler = create_file_handler(OUTPUT_LOG_FILE, append_logs, formatter)
    output_logger.addHandler(file_handler)


def initialize_logger(debug: bool, append_logs: bool):
    playbook_logger = logging.getLogger('playbook')
    playbook_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # output to console
    if not has_stdout_handler(playbook_logger):
        console_handler = logging.StreamHandler(sys.stdout)  # Explicitly target stdout
        console_formatter = ColoredFormatter(PLAYBOOK_CONSOLE_FORMAT, datefmt=DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        playbook_logger.addHandler(console_handler)

    # plain text output
    file_formatter = logging.Formatter(DEFAULT_FILE_FORMAT, datefmt=DATE_FORMAT)
    file_handler = create_file_handler(PLAYBOOK_LOG_FILE, append_logs, file_formatter)
    playbook_logger.addHandler(file_handler)
    playbook_logger.propagate = False

    return playbook_logger


def initialize_json_logger(json: bool, append_logs: bool):
    if not json:
        return None
    json_logger = logging.getLogger('json')
    json_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    file_handler = create_file_handler(JSON_LOG_FILE, append_logs, formatter)
    json_logger.addHandler(file_handler)

    return json_logger


def create_file_handler(
    file_name: str, append_logs: bool, formatter: logging.Formatter
) -> logging.FileHandler:
    mode = 'a' if append_logs else 'w'
    file_handler = logging.FileHandler(file_name, mode=mode)
    file_handler.setFormatter(formatter)
    return file_handler


def has_stdout_handler(logger: logging.Logger) -> bool:
    """
    Checks if a logger already has a StreamHandler directed to stdout.

    """
    return any(
        isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout
        for handler in logger.handlers
    )
