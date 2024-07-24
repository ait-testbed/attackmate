import pytest
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path
import yaml
from attackmate.__main__ import parse_playbook

# import other frunciotn sfrom other modules to mock: yaml _load?


# Mock Playbook class for validation
class MockPlaybook:
    @staticmethod
    def model_validate(data):
        return 'MockPlaybookObject'


# Sample YAML content for the playbook
sample_playbook_yaml = """
###
commands:
  - type: shell
    cmd: ls

"""


@pytest.fixture
def mock_logger():
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def mock_playbook_file(tmp_path):
    # Create a temporary playbook file with sample YAML content
    playbook_file = tmp_path / 'playbook.yml'
    playbook_file.write_text(sample_playbook_yaml)
    return playbook_file


def test_parse_playbook_valid_file(mock_logger, mock_playbook_file):
    with patch(
        'attackmate.__main__.yaml.safe_load', return_value=yaml.safe_load(sample_playbook_yaml)
    ), patch('attackmate.__main__.Playbook', MockPlaybook):

        # Call the function with the path to the temporary playbook file
        result = parse_playbook(str(mock_playbook_file), mock_logger)

        # Assertions
        assert result == 'MockPlaybookObject'


def test_parse_playbook_nonexistent_file(mock_logger):
    non_existent_file = Path('/non/existent/path/playbook.yml')

    with pytest.raises(SystemExit):
        parse_playbook(str(non_existent_file), mock_logger)
    mock_logger.error.assert_called_with(
        f"Error: Playbook file not found under '{non_existent_file}' or in the current directory or in '/etc/attackmate/playbooks'"
    )
