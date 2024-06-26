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
        'key1': 'value1',
        'key2': 'value2'
    }


@pytest.fixture
def config_content(mock_config):
    return yaml.dump(mock_config)


@pytest.fixture
def mock_config_class(mock_config):
    return Config.model_validate(mock_config)


def mock_file_open(file_dict):
    """
    Helper function to mock open for specific files.
    Takes a dictionary of file_path: file_content and returns a mock_open object
    that returns the corresponding file_content when the file_path is opened.
    """
    mock_open_instance = mock_open()
    handle_dict = {file: mock_open(read_data=content).return_value for file, content in file_dict.items()}

    def side_effect(file, *args, **kwargs):
        if file in handle_dict:
            return handle_dict[file]
        raise FileNotFoundError(f"No such file or directory: '{file}'")

    mock_open_instance.side_effect = side_effect
    return mock_open_instance


@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open, read_data='key1: value1\nkey2: value2')
@patch('attackmate.schemas.config.Config')
def test_parse_config_no_file(mock_config, mock_open, mock_getsize, mock_logger, mock_config_class):
    mock_getsize.return_value = 10
    mock_config.model_validate.return_value = mock_config_class

    cfg = parse_config(None, mock_logger)

    assert cfg == mock_config_class
    mock_logger.debug.assert_any_call('Config file .attackmate.yml loaded')


@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open, read_data='key1: value1\nkey2: value2')
@patch('attackmate.schemas.config.Config')
def test_parse_config_specified_file(mock_config, mock_open, mock_getsize, mock_logger, mock_config_class):
    config_file = '/path/to/config.yml'
    mock_getsize.return_value = 10
    mock_config.model_validate.return_value = mock_config_class

    cfg = parse_config(config_file, mock_logger)

    assert cfg == mock_config_class
    mock_logger.debug.assert_any_call(f'Config file {config_file} loaded')


@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open)
def test_parse_config_file_not_found(mock_getsize, mock_open, mock_logger):
    mock_getsize.side_effect = OSError

    with pytest.raises(SystemExit):
        parse_config('/path/to/nonexistent/config.yml', mock_logger)

    mock_logger.error.assert_any_call('Error: Could not open file /path/to/nonexistent/config.yml')


@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open)
@patch('attackmate.schemas.config.Config')
def test_parse_config_empty_file(mock_config, mock_open, mock_getsize, mock_logger):
    mock_getsize.return_value = 0
    mock_config.return_value = Config()

    cfg = parse_config('/path/to/empty/config.yml', mock_logger)

    assert cfg == Config()
    mock_logger.debug.assert_any_call('Config file /path/to/empty/config.yml is empty. Using default config.')


@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open)
def test_parse_config_yaml_parser_error(mock_open, mock_getsize, mock_logger):
    mock_getsize.return_value = 10
    mock_open.side_effect = yaml.parser.ParserError('Error parsing YAML')

    with pytest.raises(SystemExit):
        parse_config('/path/to/invalid/config.yml', mock_logger)

    mock_logger.error.assert_called_once()


@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open, read_data='###\n###\n')
@patch('attackmate.schemas.config.Config')
def test_parse_config_only_comments(mock_config, mock_open, mock_getsize, mock_logger):
    mock_getsize.return_value = 10
    mock_config.return_value = Config()
    cfg = parse_config('/path/to/comment_only/config.yml', mock_logger)

    assert cfg == Config()
    mock_logger.debug.assert_any_call(
        'Config file /path/to/comment_only/config.yml is empty. Using default config.')


@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open)
def test_parse_config_no_file_all_defaults_empty(mock_open, mock_getsize, mock_logger):
    mock_getsize.side_effect = [0, 0, 0]  # simulate all default config files being empty
    cfg = parse_config(None, mock_logger)

    assert isinstance(cfg, Config)
    mock_logger.debug.assert_any_call(
        'No config-file found or the default attackmate.yml was empty. Using default-config')


@patch('os.path.getsize')
@patch('builtins.open')
@patch('attackmate.schemas.config.Config')
def test_parse_config_one_default_empty_others_comments(mock_config, mock_open, mock_logger):
    # simulate the first default config file being empty, and the other two containing comments
    mock_open.side_effect = [
        mock_open(read_data='').return_value,
        mock_open(read_data='###\n###\n').return_value,
        mock_open(read_data='###').return_value
    ]
    cfg = parse_config(None, mock_logger)

    assert cfg == Config()
    mock_logger.debug.assert_any_call(
        'No config-file found or the default attackmate.yml was empty. Using default-config')


@patch('os.path.getsize')
@patch('builtins.open')
@patch('os.environ', {'HOME': '/home/user'})
def test_parse_config_first_default_has_values(mock_open, mock_getsize, mock_logger):
    valid_config_data = 'key1: value1\nkey2: value2'
    file_data = {
        '.attackmate.yml': valid_config_data,
        '/home/user/.config/attackmate.yml': '',
        '/etc/attackmate.yml': ''
    }
    mock_getsize.side_effect = lambda path: 10 if path == '.attackmate.yml' else 0
    mock_open_instance = mock_file_open(file_data)
    mock_open.side_effect = mock_open_instance.side_effect
    cfg = parse_config(None, mock_logger)

    assert isinstance(cfg, Config)
    mock_logger.debug.assert_any_call('Config file .attackmate.yml loaded')


@patch('os.path.getsize')
@patch('builtins.open')
@patch('os.environ', {'HOME': '/home/user'})
def test_parse_config_middle_default_has_values(mock_open, mock_getsize, mock_logger):
    valid_config_data = 'key1: value1\nkey2: value2'
    file_data = {
        '.attackmate.yml': '',
        '/home/user/.config/attackmate.yml': valid_config_data,
        '/etc/attackmate.yml': ''
    }
    mock_getsize.side_effect = lambda path: 10 if path == '/home/user/.config/attackmate.yml' else 0
    mock_open_instance = mock_file_open(file_data)
    mock_open.side_effect = mock_open_instance.side_effect
    cfg = parse_config(None, mock_logger)

    assert isinstance(cfg, Config)
    mock_logger.debug.assert_any_call('Config file /home/user/.config/attackmate.yml loaded')


@patch('os.path.getsize')
@patch('builtins.open')
@patch('os.environ', {'HOME': '/home/user'})
def test_parse_config_last_default_has_values(mock_open, mock_getsize, mock_logger):
    valid_config_data = 'key1: value1\nkey2: value2'
    file_data = {
        '.attackmate.yml': '',
        '/home/user/.config/attackmate.yml': '',
        '/etc/attackmate.yml': valid_config_data
    }
    mock_getsize.side_effect = lambda path: 0 if path != '/etc/attackmate.yml' else 10
    mock_open_instance = mock_file_open(file_data)
    mock_open.side_effect = mock_open_instance.side_effect
    cfg = parse_config(None, mock_logger)

    assert isinstance(cfg, Config)
    mock_logger.debug.assert_any_call('Config file /etc/attackmate.yml loaded')
