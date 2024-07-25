import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from attackmate.executors.sliver.sliverexecutor import SliverExecutor
from sliver.protobuf import client_pb2


@pytest.fixture
def setup_executor():
    # Mock dependencies and create a SliverExecutor instance
    pm = MagicMock()  # Mock ProcessManager
    varstore = MagicMock()  # Mock VariableStore
    sliver_config = MagicMock()  # Mock SliverConfig
    sliver_config.config_file = None
    executor = SliverExecutor(pm, varstore=varstore, sliver_config=sliver_config)
    return executor


@pytest.fixture
def temp_file():
    # Create a temporary file and ensure it's removed after the test
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()  # Close the file so it can be opened later
    yield temp_file.name
    os.remove(temp_file.name)


def test_save_implant_with_filepath(setup_executor, temp_file):
    executor = setup_executor
    implant = client_pb2.Generate()
    implant.File.Data = b'Test data'

    # Mock os.path.exists to return False so the file is created
    with patch('os.path.exists', return_value=False):
        result = executor.save_implant(implant, temp_file)

    assert result == temp_file
    assert os.path.exists(temp_file)

    with open(temp_file, 'rb') as f:
        assert f.read() == b'Test data'


def test_save_implant_without_filepath(setup_executor):
    executor = setup_executor
    implant = client_pb2.Generate()
    implant.File.Data = b'Test data'

    # Mock tempfile.NamedTemporaryFile
    with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
        # Create a mock file object
        mock_tempfile_instance = MagicMock()
        mock_tempfile_instance.name = 'temp_file.bin'
        mock_tempfile.return_value = mock_tempfile_instance

        # Mock os.path.exists to return False so the file is created
        with patch('os.path.exists', return_value=False), patch('os.remove') as mock_remove:

            result = executor.save_implant(implant)

        assert result == 'temp_file.bin'
        assert os.path.exists('temp_file.bin')

        with open('temp_file.bin', 'rb') as f:
            assert f.read() == b'Test data'

        mock_remove.assert_not_called()

        os.remove('temp_file.bin')


def test_save_implant_overwrite_file(setup_executor, temp_file):
    executor = setup_executor
    implant = client_pb2.Generate()
    implant.File.Data = b'New data'

    # Create a file to be overwritten
    with open(temp_file, 'wb') as f:
        f.write(b'Old data')

    result = executor.save_implant(implant, temp_file)

    assert result == temp_file
    assert os.path.exists(temp_file)

    with open(temp_file, 'rb') as f:
        assert f.read() == b'New data'


def test_save_implant_set_variable_called(setup_executor, temp_file):
    executor = setup_executor
    implant = client_pb2.Generate()
    implant.File.Data = b'Test data'

    # Mock os.path.exists to return False so the file is created
    with patch('os.path.exists', return_value=False):
        executor.save_implant(implant, temp_file)

    executor.varstore.set_variable.assert_called_once_with('LAST_SLIVER_IMPLANT', temp_file)
