import pytest
import re
import vcr
from pydantic import ValidationError
from attackmate.execexception import ExecException
from attackmate.executors.bettercap.bettercapexecutor import BettercapExecutor
from attackmate.schemas.config import BettercapConfig
from attackmate.schemas.bettercap import BettercapCommand
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.result import Result


@pytest.fixture
def bettercap_config():
    ret_dict: dict[str, BettercapConfig] = {}
    config = BettercapConfig(url='http://127.0.0.1:8081', username='user', password='pass')
    ret_dict['default'] = config
    return ret_dict


@pytest.fixture
def varstore():
    return VariableStore()


@pytest.fixture
def pm():
    return ProcessManager()


@pytest.fixture
def executor(bettercap_config, varstore, pm) -> BettercapExecutor:
    # Mock dependencies and create a SliverExecutor instance
    return BettercapExecutor(pm, varstore=varstore, bettercap_config=bettercap_config)


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_events.yaml')
async def test_bettercapexecutor_get_events(executor):
    config = BettercapCommand(cmd='get_events', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('[{"tag":"sys.log"')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_module.yaml')
async def test_bettercapexecutor_get_session_module(executor):
    config = BettercapCommand(cmd='get_session_modules', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('[{"name":"any.proxy"')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_env.yaml')
async def test_bettercapexecutor_get_session_env(executor):
    config = BettercapCommand(cmd='get_session_env', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"data":{"$":"')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_gateway.yaml')
async def test_bettercapexecutor_get_session_gateway(executor):
    config = BettercapCommand(cmd='get_session_gateway', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"ipv4":"')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_hid.yaml')
async def test_bettercapexecutor_get_session_hid(executor):
    config = BettercapCommand(cmd='get_session_hid', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"devices":[')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_ble.yaml')
async def test_bettercapexecutor_get_session_ble(executor):
    config = BettercapCommand(cmd='get_session_ble', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"devices":[')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_ble_with_mac.yaml')
async def test_bettercapexecutor_get_session_ble_with_mac(executor):
    config = BettercapCommand(cmd='get_session_ble', type='bettercap')
    config.mac = '00:AA:BB:CC:DD:33'
    # the backend /session/ble/<mac> seems currently broken?
    with pytest.raises(ExecException):
        await executor._exec_cmd(config)


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_interface.yaml')
async def test_bettercapexecutor_get_session_interface(executor):
    config = BettercapCommand(cmd='get_session_interface', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"ipv4":"')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_lan.yaml')
async def test_bettercapexecutor_get_session_lan(executor):
    config = BettercapCommand(cmd='get_session_lan', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"hosts":[')
    assert result.returncode == 0


# This check crashes bettercap
#
# @vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_lan_with_mac.yaml')
# def test_bettercapexecutor_get_session_lan_with_mac(executor):
#     config = BettercapGetSessionLanCommand(cmd='get_session_lan', type='bettercap')
#     config.mac = "00:AA:BB:CC:DD:33"
#     result: Result = executor._exec_cmd(config)
#     assert result.stdout.startswith('{"hosts":[')
#     assert result.returncode == 0

@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_options.yaml')
async def test_bettercapexecutor_get_session_options(executor):
    config = BettercapCommand(cmd='get_session_options', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"InterfaceName":')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_packets.yaml')
async def test_bettercapexecutor_get_session_packets(executor):
    config = BettercapCommand(cmd='get_session_packets', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"stats":{"sent":')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_started_at.yaml')
async def test_bettercapexecutor_get_session_started_at(executor):
    config = BettercapCommand(cmd='get_session_started_at', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert re.search(r"^\"\d{4}-\d{2}-\d{2}", result.stdout)
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_wifi.yaml')
async def test_bettercapexecutor_get_session_wifi(executor):
    config = BettercapCommand(cmd='get_session_wifi', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"aps":')
    assert result.returncode == 0


# This check crashes bettercap
#
# @vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_session_wifi_with_mac.yaml')
# def test_bettercapexecutor_get_session_wifi_with_mac(executor):
#    config = BettercapGetSessionWifiCommand(cmd='get_session_wifi', type='bettercap')
#    config.mac = "00:AA:BB:CC:DD:33"
#    result: Result = executor._exec_cmd(config)
#    assert result.stdout.startswith('{"aps":')
#    assert result.returncode == 0

@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_file.yaml')
async def test_bettercapexecutor_get_file(executor):
    config = BettercapCommand(cmd='get_file', filename='/etc/services', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('# Network services, Internet')
    assert result.returncode == 0


@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_get_file-nofile.yaml')
def test_bettercapexecutor_get_file_without_filename(executor):
    with pytest.raises(ValidationError) as e_info:
        BettercapCommand(cmd='get_file', type='bettercap')
    assert str(e_info.value).find('Value error, get_file requires the parameter filename')


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_post_api_session.yaml')
async def test_bettercapexecutor_post_api_session(executor):
    data = {'cmd': 'help'}
    config = BettercapCommand(cmd='post_api_session', data=data, type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('{"success":true,"msg":')
    assert result.returncode == 0


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_post_api_session-nodata.yaml')
async def test_bettercapexecutor_post_api_session_without_data(executor):
    with pytest.raises(ValidationError) as e_info:
        BettercapCommand(cmd='post_api_session', type='bettercap')
    assert str(e_info.value).find('Value error, post_api_session requires the parameter data')


@pytest.mark.asyncio
@vcr.use_cassette('test/fixtures/vcr_cassettes/bettercap_delete_api_events.yaml')
async def test_bettercapexecutor_delete_api_events(executor):
    config = BettercapCommand(cmd='delete_api_events', type='bettercap')
    result: Result = await executor._exec_cmd(config)
    assert result.stdout.startswith('')
    assert result.returncode == 0
