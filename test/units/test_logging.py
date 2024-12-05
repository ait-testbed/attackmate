from unittest.mock import patch, MagicMock
from logging import FileHandler
import pytest
from attackmate.logging_setup import initialize_output_logger, initialize_logger, initialize_json_logger


@pytest.fixture
def mock_file_handler():
    with patch('logging.FileHandler', spec=FileHandler) as mock_file_handler:
        yield mock_file_handler


def test_initialize_output_logger_append_mode(mock_file_handler):
    mock_handler_instance = MagicMock()
    mock_file_handler.return_value = mock_handler_instance

    initialize_output_logger(debug=True, append_logs=True)

    mock_file_handler.assert_called_once_with('output.log', mode='a')
    mock_handler_instance.setFormatter.assert_called_once()


def test_initialize_logger_append_mode(mock_file_handler):
    mock_handler_instance = MagicMock()
    mock_file_handler.return_value = mock_handler_instance

    initialize_logger(debug=False, append_logs=True)

    mock_file_handler.assert_any_call('attackmate.log', mode='a')
    mock_handler_instance.setFormatter.assert_called()


def test_initialize_json_logger_append_mode(mock_file_handler):
    mock_handler_instance = MagicMock()
    mock_file_handler.return_value = mock_handler_instance

    initialize_json_logger(json=True, append_logs=True)

    mock_file_handler.assert_called_once_with('attackmate.json', mode='a')
    mock_handler_instance.setFormatter.assert_called_once()
