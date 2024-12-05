import pytest
from unittest.mock import patch, MagicMock
from attackmate.logging_setup import create_file_handler


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
