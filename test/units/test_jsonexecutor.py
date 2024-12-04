import pytest
from unittest.mock import patch, mock_open, MagicMock
import json
import logging
from attackmate.variablestore import VariableStore
from attackmate.executors.common.jsonexecutor import JsonExecutor
from attackmate.schemas.json import JsonCommand
from attackmate.processmanager import ProcessManager


@pytest.fixture
def mock_logger():
    logger = MagicMock(spec=logging.Logger)
    return logger


@pytest.fixture
def mock_json_file():
    """
    Mock JSON file content to be used in tests.
    """
    return json.dumps({'foo': 'bar', 'hello': 'world', 'my_list': ['cthulu', 'azatoth']})


class TestJsonExecutor:
    def setup_method(self, method):
        self.varstore = VariableStore()
        self.process_manager = ProcessManager()
        self.json_executor = JsonExecutor(self.process_manager, varstore=self.varstore)

    def test_successful_json_load(self, mock_json_file, mock_logger):
        """
        Test successful loading and parsing of a JSON file.
        """
        # Mock the open function
        with patch('builtins.open', mock_open(read_data=mock_json_file)):
            self.json_executor.logger = mock_logger

            command = JsonCommand(type='json', cmd='mockfile.json', varstore=True)

            result = self.json_executor._exec_cmd(command)

            assert result.returncode == 0
            assert result.stdout == {'foo': 'bar', 'hello': 'world', 'my_list': ['cthulu', 'azatoth']}
            assert self.varstore.get_variable('FOO') == 'bar'
            assert self.varstore.get_variable('HELLO') == 'world'
            assert self.varstore.get_variable('MY_LIST') == ['cthulu', 'azatoth']
            mock_logger.info.assert_any_call("Successfully loaded JSON file: 'mockfile.json'")

    def test_file_not_found(self, mock_logger):
        """
        Test behavior when the specified JSON file is not found.
        """
        # Mock the open function to raise a FileNotFoundError
        with patch('builtins.open', side_effect=FileNotFoundError):
            self.json_executor.logger = mock_logger

            command = JsonCommand(type='json', cmd='nonexistent.json', varstore=False)

            result = self.json_executor._exec_cmd(command)

            assert result.returncode == 1
            assert "File 'nonexistent.json' not found" in result.stdout
            mock_logger.error.assert_called_with("File 'nonexistent.json' not found")

    def test_invalid_json(self, mock_logger):
        """
        Test behavior when the JSON file contains invalid syntax.
        """
        # Mock the open function with invalid JSON content
        with patch('builtins.open', mock_open(read_data='{invalid_json}')):
            self.json_executor.logger = mock_logger

            command = JsonCommand(type='json', cmd='invalid.json', varstore=False)

            result = self.json_executor._exec_cmd(command)

            assert result.returncode == 1
            assert "Error parsing JSON file 'invalid.json'" in result.stdout

    def test_unexpected_error(self, mock_logger):
        """
        Test behavior when an unexpected exception occurs during file processing.
        """
        # Mock the open function to raise a generic exception
        with patch('builtins.open', side_effect=Exception('Unexpected error')):
            # Inject the mock logger into the JsonExecutor instance
            self.json_executor.logger = mock_logger

            # Create a mock JsonCommand
            command = JsonCommand(type='json', cmd='unexpected.json', varstore=False)

            # Execute the command
            result = self.json_executor._exec_cmd(command)

            # Assertions
            assert result.returncode == 1
            assert 'Unexpected error: Unexpected error' in result.stdout
            mock_logger.error.assert_called_with
