import pytest
from unittest.mock import MagicMock, patch
from pymetasploit3.msfrpc import MsfAuthError

from attackmate.execexception import ExecException
from attackmate.executors.metasploit.msfexecutor import MsfModuleExecutor
from attackmate.executors.metasploit.msfsessionexecutor import MsfSessionExecutor
from attackmate.executors.metasploit.msfpayloadexecutor import MsfPayloadExecutor
from attackmate.executors.metasploit.msfsessionstore import MsfSessionStore
from attackmate.schemas.config import MsfConfig
from attackmate.schemas.metasploit import MsfModuleCommand, MsfSessionCommand, MsfPayloadCommand
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


@pytest.fixture
def varstore():
    return VariableStore()


@pytest.fixture
def pm():
    return ProcessManager()


@pytest.fixture
def sessionstore(varstore):
    return MsfSessionStore(varstore)


@pytest.fixture
def single_config():
    return {'default': MsfConfig(password='secret', server='127.0.0.1')}


@pytest.fixture
def multi_config():
    return {
        'server1': MsfConfig(password='pw1', server='127.0.0.1'),
        'server2': MsfConfig(password='pw2', server='127.0.0.2'),
    }


@pytest.fixture
def executor_single(pm, varstore, sessionstore, single_config):
    return MsfModuleExecutor(pm, varstore=varstore, msf_config=single_config, msfsessionstore=sessionstore)


@pytest.fixture
def executor_multi(pm, varstore, sessionstore, multi_config):
    return MsfModuleExecutor(pm, varstore=varstore, msf_config=multi_config, msfsessionstore=sessionstore)


# --- _resolve_connection ---

class TestMsfResolveConnection:
    def test_no_connection_field_uses_first_entry(self, executor_single):
        cmd = MsfModuleCommand(type='msf-module', cmd='exploit/multi/handler')
        assert executor_single._resolve_connection(cmd) == 'default'

    def test_no_connection_field_uses_first_of_multiple(self, executor_multi):
        cmd = MsfModuleCommand(type='msf-module', cmd='exploit/multi/handler')
        assert executor_multi._resolve_connection(cmd) == 'server1'

    def test_explicit_connection_overrides_default(self, executor_multi):
        cmd = MsfModuleCommand(type='msf-module', cmd='exploit/multi/handler', connection='server2')
        assert executor_multi._resolve_connection(cmd) == 'server2'

    def test_empty_config_raises(self, pm, varstore, sessionstore):
        executor = MsfModuleExecutor(pm, varstore=varstore, msf_config={}, msfsessionstore=sessionstore)
        cmd = MsfModuleCommand(type='msf-module', cmd='exploit/multi/handler')
        with pytest.raises(ExecException, match='No MSF connections configured'):
            executor._resolve_connection(cmd)


# --- _get_client ---

class TestMsfGetClient:
    def test_connects_lazily_on_first_call(self, executor_single):
        with patch('attackmate.executors.metasploit.msfclientmixin.MsfRpcClient') as mock_cls:
            mock_cls.return_value = MagicMock()
            executor_single._get_client('default')
            mock_cls.assert_called_once()
            assert 'default' in executor_single._msf_clients

    def test_passes_config_fields_to_rpc_client(self, executor_single):
        with patch('attackmate.executors.metasploit.msfclientmixin.MsfRpcClient') as mock_cls:
            mock_cls.return_value = MagicMock()
            executor_single._get_client('default')
            call_kwargs = mock_cls.call_args[1]
            assert call_kwargs['password'] == 'secret'
            assert call_kwargs['server'] == '127.0.0.1'

    def test_returns_cached_client_on_subsequent_calls(self, executor_single):
        with patch('attackmate.executors.metasploit.msfclientmixin.MsfRpcClient') as mock_cls:
            mock_cls.return_value = MagicMock()
            first = executor_single._get_client('default')
            second = executor_single._get_client('default')
            mock_cls.assert_called_once()
            assert first is second

    def test_creates_independent_client_per_connection(self, executor_multi):
        with patch('attackmate.executors.metasploit.msfclientmixin.MsfRpcClient') as mock_cls:
            mock_cls.side_effect = [MagicMock(), MagicMock()]
            c1 = executor_multi._get_client('server1')
            c2 = executor_multi._get_client('server2')
            assert c1 is not c2
            assert mock_cls.call_count == 2

    def test_raises_for_unknown_connection_name(self, executor_multi):
        with pytest.raises(ExecException, match="MSF connection 'unknown' not found in config"):
            executor_multi._get_client('unknown')

    def test_raises_on_io_error(self, executor_single):
        with patch('attackmate.executors.metasploit.msfclientmixin.MsfRpcClient',
                   side_effect=IOError('connection refused')):
            with pytest.raises(ExecException, match='MSF connection failed'):
                executor_single._get_client('default')

    def test_raises_on_auth_error(self, executor_single):
        with patch('attackmate.executors.metasploit.msfclientmixin.MsfRpcClient',
                   side_effect=MsfAuthError('bad password')):
            with pytest.raises(ExecException, match='MSF authentication failed'):
                executor_single._get_client('default')


# --- command connection field ---

class TestMsfCommandConnectionField:
    def test_msf_module_command_defaults_to_none(self):
        cmd = MsfModuleCommand(type='msf-module', cmd='exploit/multi/handler')
        assert cmd.connection is None

    def test_msf_module_command_accepts_connection(self):
        cmd = MsfModuleCommand(type='msf-module', cmd='exploit/multi/handler', connection='server2')
        assert cmd.connection == 'server2'

    def test_msf_session_command_accepts_connection(self):
        cmd = MsfSessionCommand(type='msf-session', cmd='sysinfo', session='my_session', connection='server2')
        assert cmd.connection == 'server2'

    def test_msf_payload_command_accepts_connection(self):
        cmd = MsfPayloadCommand(
            type='msf-payload',
            cmd='windows/meterpreter/reverse_tcp',
            connection='server1')
        assert cmd.connection == 'server1'


# --- mixin wiring for all three MSF executors ---

class TestMsfExecutorMixinWiring:
    def test_module_executor_has_resolve_and_get_client(self, pm, varstore, sessionstore, multi_config):
        executor = MsfModuleExecutor(
            pm,
            varstore=varstore,
            msf_config=multi_config,
            msfsessionstore=sessionstore)
        assert hasattr(executor, '_resolve_connection')
        assert hasattr(executor, '_get_client')

    def test_session_executor_has_resolve_and_get_client(self, pm, varstore, sessionstore, multi_config):
        executor = MsfSessionExecutor(
            pm,
            varstore=varstore,
            msf_config=multi_config,
            msfsessionstore=sessionstore)
        assert hasattr(executor, '_resolve_connection')
        assert hasattr(executor, '_get_client')

    def test_payload_executor_has_resolve_and_get_client(self, pm, varstore, multi_config):
        executor = MsfPayloadExecutor(pm, varstore=varstore, msf_config=multi_config)
        assert hasattr(executor, '_resolve_connection')
        assert hasattr(executor, '_get_client')

    def test_session_executor_resolves_connection(self, pm, varstore, sessionstore, multi_config):
        executor = MsfSessionExecutor(
            pm,
            varstore=varstore,
            msf_config=multi_config,
            msfsessionstore=sessionstore)
        cmd = MsfSessionCommand(type='msf-session', cmd='sysinfo', session='s', connection='server2')
        assert executor._resolve_connection(cmd) == 'server2'

    def test_payload_executor_resolves_connection(self, pm, varstore, multi_config):
        executor = MsfPayloadExecutor(pm, varstore=varstore, msf_config=multi_config)
        cmd = MsfPayloadCommand(
            type='msf-payload',
            cmd='windows/meterpreter/reverse_tcp',
            connection='server1')
        assert executor._resolve_connection(cmd) == 'server1'
