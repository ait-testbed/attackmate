from unittest.mock import patch, MagicMock
from attackmate.logging_setup import create_file_handler
from attackmate.logging_setup import initialize_json_logger
import logging


@patch('attackmate.logging_setup.logging.FileHandler')
def test_create_file_handler_append_mode(MockFileHandler):
    mock_handler = MagicMock()
    MockFileHandler.return_value = mock_handler

    file_name = 'test.log'
    append_logs = True
    formatter = MagicMock()

    create_file_handler(file_name, append_logs, formatter)

    MockFileHandler.assert_called_with(file_name, mode='a')
    mock_handler.setFormatter.assert_called_with(formatter)


@patch('attackmate.logging_setup.logging.FileHandler')
def test_create_file_handler_write_mode(MockFileHandler):
    mock_handler = MagicMock()
    MockFileHandler.return_value = mock_handler

    file_name = 'test.log'
    append_logs = False
    formatter = MagicMock()

    create_file_handler(file_name, append_logs, formatter)

    MockFileHandler.assert_called_with(file_name, mode='w')
    mock_handler.setFormatter.assert_called_with(formatter)

@patch('attackmate.logging_setup.logging.getLogger')
@patch('attackmate.logging_setup.logging.Formatter')
@patch('attackmate.logging_setup.create_file_handler')
def test_initialize_json_logger_when_enabled(mock_create_handler, mock_formatter, mock_get_logger):
    """
    Tests that the JSON logger is configured correctly when enabled.
    """
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_file_handler = MagicMock()
    mock_create_handler.return_value = mock_file_handler
    mock_formatter_instance = MagicMock()
    mock_formatter.return_value = mock_formatter_instance

    json_logger = initialize_json_logger(json=True, append_logs=True)

    mock_get_logger.assert_called_once_with('json')
    mock_logger.setLevel.assert_called_once_with(logging.DEBUG)

    mock_create_handler.assert_called_once_with('attackmate.json', True, mock_formatter_instance)
    mock_logger.addHandler.assert_called_once_with(mock_file_handler)


@patch('attackmate.logging_setup.logging.getLogger')
@patch('attackmate.logging_setup.create_file_handler')
def test_initialize_json_logger_when_disabled(mock_create_handler, mock_get_logger):
    """
    Tests that the JSON logger is not created and returns None when disabled.
    """
    returned_value = initialize_json_logger(json=False, append_logs=True)

    assert returned_value is None
    mock_get_logger.assert_not_called()
    mock_create_handler.assert_not_called()
