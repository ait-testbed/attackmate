import pytest
from unittest.mock import MagicMock, patch

from attackmate.execexception import ExecException
from attackmate.executors.sliver.sliverexecutor import SliverExecutor
from attackmate.executors.sliver.sliversessionexecutor import SliverSessionExecutor
from attackmate.schemas.config import SliverConfig
from attackmate.schemas.sliver import (
    SliverHttpsListenerCommand,
    SliverGenerateCommand,
    SliverSessionSimpleCommand,
)
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


@pytest.fixture
def varstore():
    return VariableStore()


@pytest.fixture
def pm():
    return ProcessManager()


@pytest.fixture
def single_config():
    return {'default': SliverConfig(config_file='/path/to/config.cfg')}


@pytest.fixture
def multi_config():
    return {
        'sliver1': SliverConfig(config_file='/path/to/cfg1.cfg'),
        'sliver2': SliverConfig(config_file='/path/to/cfg2.cfg'),
    }


@pytest.fixture
def executor_single(pm, varstore, single_config):
    return SliverExecutor(pm, varstore=varstore, sliver_config=single_config)


@pytest.fixture
def executor_multi(pm, varstore, multi_config):
    return SliverExecutor(pm, varstore=varstore, sliver_config=multi_config)


# --- _resolve_connection ---

class TestSliverResolveConnection:
    def test_no_connection_field_uses_first_entry(self, executor_single):
        cmd = SliverHttpsListenerCommand(type='sliver', cmd='start_https_listener')
        assert executor_single._resolve_connection(cmd) == 'default'

    def test_no_connection_field_uses_first_of_multiple(self, executor_multi):
        cmd = SliverHttpsListenerCommand(type='sliver', cmd='start_https_listener')
        assert executor_multi._resolve_connection(cmd) == 'sliver1'

    def test_explicit_connection_overrides_default(self, executor_multi):
        cmd = SliverHttpsListenerCommand(type='sliver', cmd='start_https_listener', connection='sliver2')
        assert executor_multi._resolve_connection(cmd) == 'sliver2'

    def test_empty_config_raises(self, pm, varstore):
        executor = SliverExecutor(pm, varstore=varstore, sliver_config={})
        cmd = SliverHttpsListenerCommand(type='sliver', cmd='start_https_listener')
        with pytest.raises(ExecException, match='No Sliver connections configured'):
            executor._resolve_connection(cmd)

    def test_session_command_connection_resolved(self, executor_multi):
        cmd = SliverSessionSimpleCommand(
            type='sliver-session',
            cmd='pwd',
            session='test',
            connection='sliver2')
        assert executor_multi._resolve_connection(cmd) == 'sliver2'


# --- _get_client ---

class TestSliverGetClient:
    def test_parses_config_file_on_first_call(self, executor_single):
        with patch('attackmate.executors.sliver.sliverclientmixin.SliverClientConfig') as mock_cfg, \
                patch('attackmate.executors.sliver.sliverclientmixin.SliverClient'):
            mock_cfg.parse_config_file.return_value = MagicMock()
            executor_single._get_client('default')
            mock_cfg.parse_config_file.assert_called_once_with('/path/to/config.cfg')

    def test_creates_sliver_client_on_first_call(self, executor_single):
        with patch('attackmate.executors.sliver.sliverclientmixin.SliverClientConfig') as mock_cfg, \
                patch('attackmate.executors.sliver.sliverclientmixin.SliverClient') as mock_client_cls:
            mock_cfg.parse_config_file.return_value = MagicMock()
            mock_client_cls.return_value = MagicMock()
            executor_single._get_client('default')
            mock_client_cls.assert_called_once()
            assert 'default' in executor_single._sliver_clients

    def test_returns_cached_client_on_subsequent_calls(self, executor_single):
        with patch('attackmate.executors.sliver.sliverclientmixin.SliverClientConfig') as mock_cfg, \
                patch('attackmate.executors.sliver.sliverclientmixin.SliverClient') as mock_client_cls:
            mock_cfg.parse_config_file.return_value = MagicMock()
            mock_client_cls.return_value = MagicMock()
            first = executor_single._get_client('default')
            second = executor_single._get_client('default')
            mock_cfg.parse_config_file.assert_called_once()
            assert first is second

    def test_creates_independent_client_per_connection(self, executor_multi):
        with patch('attackmate.executors.sliver.sliverclientmixin.SliverClientConfig') as mock_cfg, \
                patch('attackmate.executors.sliver.sliverclientmixin.SliverClient') as mock_client_cls:
            mock_cfg.parse_config_file.return_value = MagicMock()
            mock_client_cls.side_effect = [MagicMock(), MagicMock()]
            c1 = executor_multi._get_client('sliver1')
            c2 = executor_multi._get_client('sliver2')
            assert c1 is not c2
            assert mock_client_cls.call_count == 2

    def test_raises_for_unknown_connection_name(self, executor_multi):
        with pytest.raises(ExecException, match="Sliver connection 'unknown' not found in config"):
            executor_multi._get_client('unknown')

    def test_raises_when_config_file_is_none(self, pm, varstore):
        executor = SliverExecutor(pm, varstore=varstore,
                                  sliver_config={'no_file': SliverConfig(config_file=None)})
        with pytest.raises(ExecException, match='has no config_file'):
            executor._get_client('no_file')


# --- command connection field ---

class TestSliverCommandConnectionField:
    def test_https_listener_defaults_to_none(self):
        cmd = SliverHttpsListenerCommand(type='sliver', cmd='start_https_listener')
        assert cmd.connection is None

    def test_https_listener_accepts_connection(self):
        cmd = SliverHttpsListenerCommand(type='sliver', cmd='start_https_listener', connection='sliver2')
        assert cmd.connection == 'sliver2'

    def test_generate_command_accepts_connection(self):
        cmd = SliverGenerateCommand(
            type='sliver', cmd='generate_implant', c2url='https://10.0.0.1', name='implant',
            connection='sliver1'
        )
        assert cmd.connection == 'sliver1'

    def test_session_command_accepts_connection(self):
        cmd = SliverSessionSimpleCommand(type='sliver-session', cmd='pwd', session='my_session',
                                         connection='sliver1')
        assert cmd.connection == 'sliver1'

    def test_session_command_connection_inherited_by_subclasses(self):
        cmd = SliverSessionSimpleCommand(type='sliver-session', cmd='ps', session='my_session',
                                         connection='sliver2')
        assert cmd.connection == 'sliver2'


# --- mixin wiring for both Sliver executors ---

class TestSliverExecutorMixinWiring:
    def test_sliver_executor_has_resolve_and_get_client(self, pm, varstore, multi_config):
        executor = SliverExecutor(pm, varstore=varstore, sliver_config=multi_config)
        assert hasattr(executor, '_resolve_connection')
        assert hasattr(executor, '_get_client')

    def test_sliver_session_executor_has_resolve_and_get_client(self, pm, varstore, multi_config):
        executor = SliverSessionExecutor(pm, varstore=varstore, sliver_config=multi_config)
        assert hasattr(executor, '_resolve_connection')
        assert hasattr(executor, '_get_client')

    def test_session_executor_resolves_connection(self, pm, varstore, multi_config):
        executor = SliverSessionExecutor(pm, varstore=varstore, sliver_config=multi_config)
        cmd = SliverSessionSimpleCommand(type='sliver-session', cmd='pwd', session='s', connection='sliver2')
        assert executor._resolve_connection(cmd) == 'sliver2'

    def test_session_executor_raises_with_no_config(self, pm, varstore):
        executor = SliverSessionExecutor(pm, varstore=varstore, sliver_config={})
        cmd = SliverSessionSimpleCommand(type='sliver-session', cmd='pwd', session='s')
        with pytest.raises(ExecException, match='No Sliver connections configured'):
            executor._resolve_connection(cmd)
