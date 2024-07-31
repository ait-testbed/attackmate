import pytest
from unittest.mock import MagicMock, patch
import subprocess
from attackmate.executors.shell.shellexecutor import ShellExecutor
from attackmate.execexception import ExecException
from attackmate.schemas.shell import ShellCommand
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


@pytest.fixture
def mock_popen():
    mock_popen_instance = MagicMock(spec=subprocess.Popen)
    mock_popen_instance.communicate.return_value = (b'stdout', b'stderr')
    with patch('subprocess.Popen', return_value=mock_popen_instance) as mock:
        yield mock, mock_popen_instance


@pytest.fixture
def mock_process_manager():
    return MagicMock(spec=ProcessManager)


@pytest.fixture
def mock_variable_store():
    return MagicMock(spec=VariableStore)


@pytest.fixture
def shell_executor(mock_process_manager, mock_variable_store):
    return ShellExecutor(mock_process_manager, mock_variable_store)


def test_exec_cmd_hex_to_ascii(mock_popen, shell_executor):
    mock_open_proc, mock_popen_instance = mock_popen
    with patch.object(shell_executor, 'open_proc', mock_open_proc):

        command = ShellCommand(
            type='shell',
            cmd='6563686f206964',
            bin=True,
        )
        shell_executor._exec_cmd(command)

        mock_open_proc.assert_called_once_with(command)
        mock_popen_instance.communicate.assert_called_once()
        expected_command = b'echo id'
        args, _ = mock_popen_instance.communicate.call_args
        assert args[0] == expected_command


def test_exec_cmd_ascii(mock_popen, shell_executor):
    mock_open_proc, mock_popen_instance = mock_popen
    with patch.object(shell_executor, 'open_proc', mock_open_proc):

        command = ShellCommand(
            type='shell',
            cmd='echo id',
            bin=False,
        )
        shell_executor._exec_cmd(command)

        mock_open_proc.assert_called_once_with(command)
        mock_popen_instance.communicate.assert_called_once()
        expected_command = b'echo id'
        args, _ = mock_popen_instance.communicate.call_args
        assert args[0] == expected_command


def test_exec_cmd_invalid_hex(mock_popen, shell_executor):
    mock_open_proc, mock_popen_instance = mock_popen
    with patch.object(shell_executor, 'open_proc', mock_open_proc):

        command = ShellCommand(
            type='shell',
            cmd='invalidhex',
            bin=True,
        )

        with pytest.raises(
            ExecException, match="only hex characters are allowed in binary mode. Command: 'invalidhex'"
        ):
            shell_executor._exec_cmd(command)
            mock_open_proc.assert_called_once_with(command)
            mock_popen_instance.communicate.assert_not_called()


def test_execution_of_hex_command(shell_executor):

    command = ShellCommand(
        type='shell',
        cmd='6563686f206964',
        bin=True,
    )

    result = shell_executor._exec_cmd(command)
    assert result.stdout == 'id\n'
