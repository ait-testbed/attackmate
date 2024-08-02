# logging_setup.py

import logging
from colorlog import ColoredFormatter


def initialize_output_logger(debug: bool):
    output_logger = logging.getLogger('output')
    if debug:
        output_logger.setLevel(logging.DEBUG)
    else:
        output_logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('output.log', mode='w')
    formatter = logging.Formatter(
        '--- %(asctime)s %(levelname)s: ---\n\n%(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    output_logger.addHandler(file_handler)


def initialize_logger(debug: bool):
    playbook_logger = logging.getLogger('playbook')
    if debug:
        playbook_logger.setLevel(logging.DEBUG)
    else:
        playbook_logger.setLevel(logging.INFO)

    # output to console
    console_handler = logging.StreamHandler()
    LOGFORMAT = '  %(asctime)s %(log_color)s%(levelname)-8s%(reset)s' '| %(log_color)s%(message)s%(reset)s'
    formatter = ColoredFormatter(LOGFORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)

    # plain text output
    playbook_logger.addHandler(console_handler)
    file_handler = logging.FileHandler('attackmate.log', mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    playbook_logger.addHandler(file_handler)

    return playbook_logger


def initialize_json_logger(json: bool):
    if not json:
        return None
    json_logger = logging.getLogger('json')
    json_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('attackmate.json', mode='w')
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    json_logger.addHandler(file_handler)

    return json_logger
