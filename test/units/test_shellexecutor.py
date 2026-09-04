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


@pytest.mark.asyncio
async def test_exec_cmd_hex_to_ascii(mock_popen, shell_executor):
    mock_open_proc, mock_popen_instance = mock_popen
    with patch.object(shell_executor, 'open_proc', mock_open_proc):

        command = ShellCommand(
            type='shell',
            cmd='6563686f206964',
            bin=True,
        )
        await shell_executor._exec_cmd(command)

        mock_open_proc.assert_called_once_with(command)
        mock_popen_instance.communicate.assert_called_once()
        expected_command = b'echo id'
        args, _ = mock_popen_instance.communicate.call_args
        assert args[0] == expected_command


@pytest.mark.asyncio
async def test_exec_cmd_ascii(mock_popen, shell_executor):
    mock_open_proc, mock_popen_instance = mock_popen
    with patch.object(shell_executor, 'open_proc', mock_open_proc):

        command = ShellCommand(
            type='shell',
            cmd='echo id',
            bin=False,
        )
        await shell_executor._exec_cmd(command)

        mock_open_proc.assert_called_once_with(command)
        mock_popen_instance.communicate.assert_called_once()
        expected_command = b'echo id'
        args, _ = mock_popen_instance.communicate.call_args
        assert args[0] == expected_command


@pytest.mark.asyncio
async def test_exec_cmd_invalid_hex(mock_popen, shell_executor):
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
            await shell_executor._exec_cmd(command)
            mock_open_proc.assert_called_once_with(command)
            mock_popen_instance.communicate.assert_not_called()


@pytest.mark.asyncio
async def test_execution_of_hex_command(shell_executor):

    command = ShellCommand(
        type='shell',
        cmd='6563686f206964',
        bin=True,
    )

    result = await shell_executor._exec_cmd(command)
    assert result.stdout == 'id\n'


@pytest.mark.asyncio
async def test_non_utf8_output_does_not_raise(mock_popen, shell_executor):
    """A command emitting a non-UTF-8 byte must not terminate the playbook.

    0xc9 without a continuation byte is not valid UTF-8. A strict decode raises
    UnicodeDecodeError, which nothing catches between _exec_cmd and main().
    """
    mock_open_proc, mock_popen_instance = mock_popen
    mock_popen_instance.communicate.return_value = (b'ok\xc9done', b'')
    with patch.object(shell_executor, 'open_proc', mock_open_proc):

        command = ShellCommand(
            type='shell',
            cmd="printf 'ok\\311done'",
            bin=False,
        )
        result = await shell_executor._exec_cmd(command)

        assert result.stdout == 'ok�done'


def test_popen_interactive_non_utf8_output_does_not_raise(shell_executor):
    """The interactive read path decodes separately and needs the same treatment."""
    reads = [b'ok\xc9done']

    def fake_read(_stdout):
        return reads.pop(0) if reads else b''

    mock_popen_instance = MagicMock()
    with patch.object(shell_executor, 'non_block_read', side_effect=fake_read):
        output = shell_executor.popen_interactive(mock_popen_instance, b'cmd\n', timeout=1)

    assert output == 'ok�done'


@pytest.mark.asyncio
async def test_execution_of_command_with_non_utf8_output(shell_executor):
    """End to end: /bin/sh printf has no \\xHH, so the octal escape is the portable one."""
    command = ShellCommand(
        type='shell',
        cmd="printf 'ok\\311done'",
        bin=False,
    )

    result = await shell_executor._exec_cmd(command)
    assert result.stdout == 'ok�done'
