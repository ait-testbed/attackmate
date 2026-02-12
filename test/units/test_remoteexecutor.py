import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from attackmate.executors.remote.remoteexecutor import RemoteExecutor
from attackmate.execexception import ExecException
from attackmate.schemas.config import RemoteConfig
from attackmate.schemas.remote import AttackMateRemoteCommand
from attackmate.result import Result


@pytest.fixture
def setup_executor():
    """Create a RemoteExecutor instance with mocked dependencies."""
    pm = MagicMock()  # Mock ProcessManager
    varstore = MagicMock()  # Mock VariableStore
    varstore.substitute = MagicMock(side_effect=lambda x: x)  # Return unchanged by default

    remote_config = {
        'primary': RemoteConfig(
            url='https://primary.example.com',
            username='user1',
            password='pass1',
            cafile='/path/to/ca.pem'
        ),
        'secondary': RemoteConfig(
            url='https://secondary.example.com',
            username='user2',
            password='pass2',
            cafile=None
        ),
        'no_auth': RemoteConfig(
            url='https://noauth.example.com',
            username=None,
            password=None,
            cafile=None
        )
    }

    executor = RemoteExecutor(pm, varstore=varstore, remote_config=remote_config)
    return executor


@pytest.fixture
def mock_remote_command():
    """Create a mock AttackMateRemoteCommand."""
    command = MagicMock(spec=AttackMateRemoteCommand)
    command.connection = 'primary'
    command.cmd = 'execute_command'
    command.type = 'remote'
    command.remote_command = MagicMock()
    command.remote_command.model_dump = MagicMock(return_value={'cmd': 'test'})
    command.playbook_yaml_path = None
    command.debug = False
    return command


@pytest.fixture
def temp_yaml_file():
    """Create a temporary YAML file and ensure it's removed after the test."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_file.write('---\ntest: playbook\n')
    temp_file.close()
    yield temp_file.name
    os.remove(temp_file.name)


class TestGetConnectionInfo:
    """Tests for _get_connection_info method."""

    def test_get_connection_info_explicit_connection(self, setup_executor, mock_remote_command):
        """Test getting connection info when connection is explicitly specified."""
        executor = setup_executor
        mock_remote_command.connection = 'secondary'

        info = executor._get_connection_info(mock_remote_command)

        assert info['name'] == 'secondary'
        assert info['url'] == 'https://secondary.example.com'
        assert info['user'] == 'user2'
        assert info['pass'] == 'pass2'
        assert info['cafile'] is None

    def test_get_connection_info_default_connection(self, setup_executor, mock_remote_command):
        """Test getting connection info when no connection specified (uses first)."""
        executor = setup_executor
        mock_remote_command.connection = None

        info = executor._get_connection_info(mock_remote_command)

        # Should use first connection in config
        assert info['name'] == 'primary'
        assert info['url'] == 'https://primary.example.com'

    def test_get_connection_info_no_auth(self, setup_executor, mock_remote_command):
        """Test getting connection info for connection without authentication."""
        executor = setup_executor
        mock_remote_command.connection = 'no_auth'

        info = executor._get_connection_info(mock_remote_command)

        assert info['name'] == 'no_auth'
        assert info['url'] == 'https://noauth.example.com'
        assert info['user'] is None
        assert info['pass'] is None
        assert info['cafile'] is None

    def test_get_connection_info_nonexistent_connection(self, setup_executor, mock_remote_command):
        """Test error when specified connection doesn't exist."""
        executor = setup_executor
        mock_remote_command.connection = 'nonexistent'

        with pytest.raises(ExecException, match="Remote connection 'nonexistent' not found"):
            executor._get_connection_info(mock_remote_command)

    def test_get_connection_info_no_config(self, mock_remote_command):
        """Test error when no remote config is provided."""
        pm = MagicMock()
        varstore = MagicMock()
        executor = RemoteExecutor(pm, varstore=varstore, remote_config={})
        mock_remote_command.connection = None

        with pytest.raises(ExecException, match='No remote connections configured'):
            executor._get_connection_info(mock_remote_command)

    def test_get_connection_info_variable_substitution(self, setup_executor, mock_remote_command):
        """Test that variable substitution is called for all config values."""
        executor = setup_executor
        executor.varstore.substitute = MagicMock(side_effect=lambda x: f'substituted_{x}')
        mock_remote_command.connection = 'primary'

        info = executor._get_connection_info(mock_remote_command)

        assert info['url'].startswith('substituted_')
        assert info['user'].startswith('substituted_')
        assert info['pass'].startswith('substituted_')
        assert info['cafile'].startswith('substituted_')


class TestSetupConnection:
    """Tests for setup_connection method."""

    @patch('attackmate.executors.remote.remoteexecutor.RemoteAttackMateClient')
    def test_setup_connection_creates_new_client(
            self, mock_client_class, setup_executor, mock_remote_command):
        """Test that a new client is created when not cached."""
        executor = setup_executor
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        client = executor.setup_connection(mock_remote_command)

        assert client == mock_client_instance
        mock_client_class.assert_called_once_with(
            server_url='https://primary.example.com',
            username='user1',
            password='pass1',
            cacert='/path/to/ca.pem'
        )
        assert executor._clients_cache['primary'] == mock_client_instance

    @patch('attackmate.executors.remote.remoteexecutor.RemoteAttackMateClient')
    def test_setup_connection_uses_cached_client(
            self, mock_client_class, setup_executor, mock_remote_command):
        """Test that cached client is reused."""
        executor = setup_executor
        cached_client = MagicMock()
        executor._clients_cache['primary'] = cached_client

        client = executor.setup_connection(mock_remote_command)

        assert client == cached_client
        mock_client_class.assert_not_called()  # Should not create new client

    @patch('attackmate.executors.remote.remoteexecutor.RemoteAttackMateClient')
    def test_setup_connection_client_creation_failure(
            self, mock_client_class, setup_executor, mock_remote_command):
        """Test error handling when client creation fails."""
        executor = setup_executor
        mock_client_class.side_effect = Exception('Connection failed')

        with pytest.raises(ExecException, match='Failed to create remote client'):
            executor.setup_connection(mock_remote_command)

    @patch('attackmate.executors.remote.remoteexecutor.RemoteAttackMateClient')
    def test_setup_connection_multiple_connections(
            self, mock_client_class, setup_executor, mock_remote_command):
        """Test that multiple different connections are cached separately."""
        executor = setup_executor
        mock_client_class.side_effect = [MagicMock(), MagicMock()]

        # Create first connection
        mock_remote_command.connection = 'primary'
        client1 = executor.setup_connection(mock_remote_command)

        # Create second connection
        mock_remote_command.connection = 'secondary'
        client2 = executor.setup_connection(mock_remote_command)

        assert client1 != client2
        assert len(executor._clients_cache) == 2
        assert 'primary' in executor._clients_cache
        assert 'secondary' in executor._clients_cache


class TestDispatchRemoteCommand:
    """Tests for _dispatch_remote_command method."""

    def test_dispatch_execute_command(self, setup_executor, mock_remote_command):
        """Test dispatching execute_command."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_client.execute_remote_command = MagicMock(return_value={'result': {'success': True}})
        mock_remote_command.cmd = 'execute_command'

        response = executor._dispatch_remote_command(mock_client, mock_remote_command)

        mock_client.execute_remote_command.assert_called_once_with(
            mock_remote_command.remote_command,
            debug=False
        )
        assert response == {'result': {'success': True}}

    def test_dispatch_execute_playbook(self, setup_executor, mock_remote_command, temp_yaml_file):
        """Test dispatching execute_playbook."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_client.execute_remote_playbook_yaml = MagicMock(return_value={'success': True})
        mock_remote_command.cmd = 'execute_playbook'
        mock_remote_command.playbook_yaml_path = temp_yaml_file

        response = executor._dispatch_remote_command(mock_client, mock_remote_command)

        mock_client.execute_remote_playbook_yaml.assert_called_once()
        call_args = mock_client.execute_remote_playbook_yaml.call_args
        assert '---' in call_args[0][0]  # Check YAML content
        assert call_args[1]['debug'] is False
        assert response == {'success': True}

    def test_dispatch_execute_playbook_file_not_found(self, setup_executor, mock_remote_command):
        """Test error when playbook file doesn't exist."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_remote_command.cmd = 'execute_playbook'
        mock_remote_command.playbook_yaml_path = '/nonexistent/file.yaml'

        with pytest.raises(ExecException, match='Playbook file not found'):
            executor._dispatch_remote_command(mock_client, mock_remote_command)

    def test_dispatch_execute_playbook_read_error(self, setup_executor, mock_remote_command):
        """Test error when playbook file cannot be read."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_remote_command.cmd = 'execute_playbook'
        mock_remote_command.playbook_yaml_path = '/path/to/file.yaml'

        with patch('builtins.open', side_effect=IOError('Permission denied')):
            with pytest.raises(ExecException, match='Failed to read playbook file'):
                executor._dispatch_remote_command(mock_client, mock_remote_command)

    def test_dispatch_unsupported_command(self, setup_executor, mock_remote_command):
        """Test error when command type is not supported."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_remote_command.cmd = 'unsupported_command'

        with pytest.raises(ExecException, match='Unsupported remote command'):
            executor._dispatch_remote_command(mock_client, mock_remote_command)

    def test_dispatch_with_debug_flag(self, setup_executor, mock_remote_command):
        """Test that debug flag is passed correctly."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_client.execute_remote_command = MagicMock(return_value={})
        mock_remote_command.cmd = 'execute_command'
        mock_remote_command.debug = True

        executor._dispatch_remote_command(mock_client, mock_remote_command)

        call_args = mock_client.execute_remote_command.call_args
        assert call_args[1]['debug'] is True


class TestProcessResponse:
    """Tests for _process_response method."""

    def test_process_response_command_success(self, setup_executor):
        """Test processing successful command response."""
        executor = setup_executor
        response_data = {
            'result': {
                'success': True,
                'stdout': 'Command output',
                'returncode': 0
            }
        }

        success, error_msg, stdout, return_code = executor._process_response(response_data)

        assert success is True
        assert error_msg is None
        assert stdout == 'Command output'
        assert return_code == 0

    def test_process_response_command_failure(self, setup_executor):
        """Test processing failed command response."""
        executor = setup_executor
        response_data = {
            'result': {
                'success': False,
                'stdout': 'Error output',
                'returncode': 1,
                'error_message': 'Command failed'
            }
        }

        success, error_msg, stdout, return_code = executor._process_response(response_data)

        assert success is False
        assert error_msg == 'Command failed'
        assert stdout == 'Error output'
        assert return_code == 1

    def test_process_response_playbook_success(self, setup_executor):
        """Test processing successful playbook response."""
        executor = setup_executor
        response_data = {
            'success': True,
            'message': 'Playbook executed successfully'
        }

        success, error_msg, stdout, return_code = executor._process_response(response_data)

        assert success is True
        assert error_msg is None
        assert '"success": true' in stdout.lower()
        assert return_code == 0

    def test_process_response_playbook_failure(self, setup_executor):
        """Test processing failed playbook response."""
        executor = setup_executor
        response_data = {
            'success': False,
            'message': 'Playbook execution failed'
        }

        success, error_msg, stdout, return_code = executor._process_response(response_data)

        assert success is False
        assert error_msg == 'Playbook execution failed'
        assert return_code == 1

    def test_process_response_no_response(self, setup_executor):
        """Test processing when no response is received."""
        executor = setup_executor

        success, error_msg, stdout, return_code = executor._process_response(None)

        assert success is False
        assert 'No response received' in error_msg
        assert stdout is None
        assert return_code == 1

    def test_process_response_unexpected_structure(self, setup_executor):
        """Test processing response with unexpected structure."""
        executor = setup_executor
        response_data = {'unexpected': 'data'}

        success, error_msg, stdout, return_code = executor._process_response(response_data)

        assert success is False
        assert 'unexpected response structure' in error_msg.lower()
        assert stdout is not None


class TestFormatOutput:
    """Tests for _format_output method."""

    def test_format_output_with_error_and_stdout(self, setup_executor):
        """Test formatting when both error and stdout exist."""
        executor = setup_executor

        result = executor._format_output(False, 'Some output', 'Error message')

        assert 'Error: Error message' in result
        assert 'Output/Response:' in result
        assert 'Some output' in result

    def test_format_output_with_error_only(self, setup_executor):
        """Test formatting when only error exists."""
        executor = setup_executor

        result = executor._format_output(False, None, 'Error message')

        assert result == 'Error: Error message'
        assert 'Output/Response:' not in result

    def test_format_output_with_stdout_only(self, setup_executor):
        """Test formatting when only stdout exists."""
        executor = setup_executor

        result = executor._format_output(True, 'Command output', None)

        assert result == 'Command output'

    def test_format_output_success_no_output(self, setup_executor):
        """Test formatting when successful with no output."""
        executor = setup_executor

        result = executor._format_output(True, None, None)

        assert result == 'Operation completed successfully.'

    def test_format_output_failure_no_output(self, setup_executor):
        """Test formatting when failed with no output."""
        executor = setup_executor

        result = executor._format_output(False, None, None)

        assert result == 'Operation failed with no output.'


class TestExecCmd:
    """Tests for _exec_cmd method."""

    @pytest.mark.asyncio
    @patch('attackmate.executors.remote.remoteexecutor.RemoteAttackMateClient')
    async def test_exec_cmd_success(self, mock_client_class, setup_executor, mock_remote_command):
        """Test successful command execution."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_client.execute_remote_command = MagicMock(return_value={
            'result': {
                'success': True,
                'stdout': 'Success output',
                'returncode': 0
            }
        })
        mock_client_class.return_value = mock_client

        result = await executor._exec_cmd(mock_remote_command)

        assert isinstance(result, Result)
        assert result.returncode == 0
        assert 'Success output' in result.stdout

    @pytest.mark.asyncio
    @patch('attackmate.executors.remote.remoteexecutor.RemoteAttackMateClient')
    async def test_exec_cmd_failure(self, mock_client_class, setup_executor, mock_remote_command):
        """Test failed command execution."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_client.execute_remote_command = MagicMock(return_value={
            'result': {
                'success': False,
                'stdout': 'Error output',
                'returncode': 1,
                'error_message': 'Command failed'
            }
        })
        mock_client_class.return_value = mock_client

        result = await executor._exec_cmd(mock_remote_command)

        assert isinstance(result, Result)
        assert result.returncode == 1
        assert 'Command failed' in result.stdout

    @pytest.mark.asyncio
    async def test_exec_cmd_exception_handling(self, setup_executor, mock_remote_command):
        """Test exception handling in exec_cmd."""
        executor = setup_executor

        # Mock setup_connection to raise an exception
        with patch.object(executor, 'setup_connection', side_effect=ExecException('Connection error')):
            result = await executor._exec_cmd(mock_remote_command)

        assert isinstance(result, Result)
        assert result.returncode == 1
        assert 'Connection error' in result.stdout

    @pytest.mark.asyncio
    @patch('attackmate.executors.remote.remoteexecutor.RemoteAttackMateClient')
    async def test_exec_cmd_unexpected_exception(
            self, mock_client_class, setup_executor, mock_remote_command):
        """Test handling of unexpected exceptions."""
        executor = setup_executor
        mock_client = MagicMock()
        mock_client.execute_remote_command = MagicMock(side_effect=RuntimeError('Unexpected error'))
        mock_client_class.return_value = mock_client

        result = await executor._exec_cmd(mock_remote_command)

        assert isinstance(result, Result)
        assert result.returncode == 1
        assert 'unexpected error' in result.stdout.lower()


class TestCleanup:
    """Tests for cleanup method."""

    def test_cleanup_with_cached_clients(self, setup_executor):
        """Test cleanup with cached clients that have close method."""
        executor = setup_executor
        mock_client1 = MagicMock()
        mock_client1.close = MagicMock()
        mock_client2 = MagicMock()
        mock_client2.close = MagicMock()

        executor._clients_cache['primary'] = mock_client1
        executor._clients_cache['secondary'] = mock_client2

        executor.cleanup()

        mock_client1.close.assert_called_once()
        mock_client2.close.assert_called_once()
        assert len(executor._clients_cache) == 0

    def test_cleanup_with_disconnect_method(self, setup_executor):
        """Test cleanup with clients that have disconnect method."""
        executor = setup_executor
        mock_client = MagicMock()
        del mock_client.close  # Remove close method
        mock_client.disconnect = MagicMock()

        executor._clients_cache['primary'] = mock_client

        executor.cleanup()

        mock_client.disconnect.assert_called_once()
        assert len(executor._clients_cache) == 0

    def test_cleanup_with_no_close_method(self, setup_executor):
        """Test cleanup with clients that have neither close nor disconnect."""
        executor = setup_executor
        mock_client = MagicMock(spec=[])  # No methods

        executor._clients_cache['primary'] = mock_client

        # Should not raise exception
        executor.cleanup()

        assert len(executor._clients_cache) == 0

    def test_cleanup_with_empty_cache(self, setup_executor):
        """Test cleanup with no cached clients."""
        executor = setup_executor

        # Should not raise exception
        executor.cleanup()

        assert len(executor._clients_cache) == 0

    def test_cleanup_with_exception(self, setup_executor):
        """Test cleanup continues even if one client raises exception."""
        executor = setup_executor
        mock_client1 = MagicMock()
        mock_client1.close = MagicMock(side_effect=Exception('Close failed'))
        mock_client2 = MagicMock()
        mock_client2.close = MagicMock()

        executor._clients_cache['primary'] = mock_client1
        executor._clients_cache['secondary'] = mock_client2

        # Should not raise exception, should handle gracefully
        executor.cleanup()

        # Both should have been attempted
        mock_client1.close.assert_called_once()
        mock_client2.close.assert_called_once()
        assert len(executor._clients_cache) == 0
