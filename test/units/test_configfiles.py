import yaml
import pytest
import logging
from unittest.mock import patch, mock_open, MagicMock
from attackmate.__main__ import parse_config
from attackmate.schemas.config import Config


@pytest.fixture
def mock_logger():
    logger = MagicMock(spec=logging.Logger)
    return logger


@pytest.fixture
def mock_config():
    return {
        "key1": "value1",
        "key2": "value2"
    }


@pytest.fixture
def config_content(mock_config):
    return yaml.dump(mock_config)


@pytest.fixture
def mock_config_class(mock_config):
    return Config.parse_obj(mock_config)


@patch("os.path.getsize")
@patch("builtins.open", new_callable=mock_open, read_data="key1: value1\nkey2: value2")
@patch("attackmate.schemas.config.Config")
def test_parse_config_no_file(mock_config, mock_open, mock_getsize, mock_logger, mock_config_class):
    mock_getsize.return_value = 10
    mock_config.parse_obj.return_value = mock_config_class

    cfg = parse_config(None, mock_logger)

    assert cfg == mock_config_class
    mock_logger.debug.assert_any_call('Config file .attackmate.yml loaded')


@patch("os.path.getsize")
@patch("builtins.open", new_callable=mock_open, read_data="key1: value1\nkey2: value2")
@patch("attackmate.schemas.config.Config")
def test_parse_config_specified_file(mock_config, mock_open, mock_getsize, mock_logger, mock_config_class):
    config_file = '/path/to/config.yml'
    mock_getsize.return_value = 10
    mock_config.parse_obj.return_value = mock_config_class

    cfg = parse_config(config_file, mock_logger)

    assert cfg == mock_config_class
    mock_logger.debug.assert_any_call(f'Config file {config_file} loaded')


@patch("os.path.getsize")
@patch("builtins.open", new_callable=mock_open)
def test_parse_config_file_not_found(mock_getsize, mock_open, mock_logger):
    mock_getsize.side_effect = OSError

    with pytest.raises(SystemExit):
        parse_config('/path/to/nonexistent/config.yml', mock_logger)

    mock_logger.error.assert_any_call('Error: Could not open file /path/to/nonexistent/config.yml')


@patch("os.path.getsize")
@patch("builtins.open", new_callable=mock_open)
@patch("attackmate.schemas.config.Config")
def test_parse_config_empty_file(mock_config, mock_open, mock_getsize, mock_logger):
    mock_getsize.return_value = 0
    mock_config.return_value = Config()

    cfg = parse_config('/path/to/empty/config.yml', mock_logger)

    assert cfg == Config()
    mock_logger.debug.assert_any_call('Config file /path/to/empty/config.yml is empty. Using default config.')


@patch("os.path.getsize")
@patch("builtins.open", new_callable=mock_open)
def test_parse_config_yaml_parser_error(mock_open, mock_getsize, mock_logger):
    mock_getsize.return_value = 10
    mock_open.side_effect = yaml.parser.ParserError("Error parsing YAML")

    with pytest.raises(SystemExit):
        parse_config('/path/to/invalid/config.yml', mock_logger)

    mock_logger.error.assert_called_once()
