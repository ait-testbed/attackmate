# logging_setup.py

import logging
import sys
from colorlog import ColoredFormatter


def create_file_handler(
    file_name: str, append_logs: bool, formatter: logging.Formatter
) -> logging.FileHandler:
    mode = 'a' if append_logs else 'w'
    file_handler = logging.FileHandler(file_name, mode=mode)
    file_handler.setFormatter(formatter)

    return file_handler


def initialize_output_logger(debug: bool, append_logs: bool):
    output_logger = logging.getLogger('output')
    if debug:
        output_logger.setLevel(logging.DEBUG)
    else:
        output_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '--- %(asctime)s %(levelname)s: ---\n\n%(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler = create_file_handler('output.log', append_logs, formatter)
    output_logger.addHandler(file_handler)


def initialize_logger(debug: bool, append_logs: bool):
    playbook_logger = logging.getLogger('playbook')
    if debug:
        playbook_logger.setLevel(logging.DEBUG)
    else:
        playbook_logger.setLevel(logging.INFO)

    # output to console
    if not any(
        isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout
        for handler in playbook_logger.handlers
    ):
        console_handler = logging.StreamHandler(sys.stdout) # Explicitly target stdout
        LOGFORMAT = '  %(asctime)s %(log_color)s%(levelname)-8s%(reset)s' '| %(log_color)s%(message)s%(reset)s'
        formatter = ColoredFormatter(LOGFORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        playbook_logger.addHandler(console_handler)

    # plain text output

    formatter2 = logging.Formatter('%(asctime)s %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = create_file_handler('attackmate.log', append_logs, formatter2)
    playbook_logger.addHandler(file_handler)
    playbook_logger.propagate = False

    return playbook_logger


def initialize_json_logger(json: bool, append_logs: bool):
    if not json:
        return None
    json_logger = logging.getLogger('json')
    json_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    file_handler = create_file_handler('attackmate.json', append_logs, formatter)
    json_logger.addHandler(file_handler)

    return json_logger

def initialize_api_logger(debug: bool, append_logs: bool):
    api_logger = logging.getLogger('attackmate_api')
    if debug:
        api_logger.setLevel(logging.DEBUG)
    else:
        api_logger.setLevel(logging.INFO)

    # Console handler for API logs
    if not any(
        isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout
        for handler in api_logger.handlers
    ):
        console_handler = logging.StreamHandler(sys.stdout)
        LOGFORMAT = '  %(asctime)s %(log_color)s%(levelname)-8s%(reset)s' '| API | %(log_color)s%(message)s%(reset)s'
        formatter = ColoredFormatter(LOGFORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        api_logger.addHandler(console_handler)

    #  File handler for API logs ?
    # api_file_formatter = logging.Formatter('%(asctime)s %(levelname)s [API] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # api_file_handler = create_file_handler('attackmate_api.log', append_logs, api_file_formatter)
    # api_logger.addHandler(api_file_handler)

    # Prevent propagation to avoid duplicate logs if root logger also has handlers
    api_logger.propagate = False

    return api_logger
