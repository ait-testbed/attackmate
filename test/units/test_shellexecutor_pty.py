import os
import pickle

import pytest
from pydantic import ValidationError

from attackmate.execexception import ExecException
from attackmate.executors.shell.shellexecutor import ShellExecutor
from attackmate.executors.shell.ptysession import PtySession
from attackmate.executors.shell.sessionstore import SessionStore
from attackmate.processmanager import ProcessManager
from attackmate.schemas.shell import ShellCommand
from attackmate.variablestore import VariableStore

pytestmark = pytest.mark.skipif(os.name != 'posix', reason='pty requires a Unix-like OS')

PROMPTS = ['# ', '$ ']


@pytest.fixture
def shell_executor():
    executor = ShellExecutor(ProcessManager(), VariableStore())
    try:
        yield executor
    finally:
        executor.cleanup()


def pty_command(cmd: str, **kwargs) -> ShellCommand:
    options = dict(type='shell', cmd=cmd, pty=True, command_timeout=5, prompts=PROMPTS)
    options.update(kwargs)
    return ShellCommand(**options)


# --- schema -----------------------------------------------------------------


@pytest.mark.parametrize(
    'options, expected',
    [
        ({}, False),
        ({'pty': True}, True),
        ({'pty': True, 'expand_keys': False}, False),
        ({'pty': False, 'expand_keys': True}, True),
    ],
)
def test_expand_keys_defaults_to_pty(options, expected):
    """On by default for pty only, but always explicitly overridable."""
    assert ShellCommand(type='shell', cmd='x', **options).expand_keys is expected


def test_expand_keys_survives_the_remote_hop():
    """attackmate-client dumps with exclude_none, which would drop a None default.

    A remote executor re-validates the dumped dict, so the resolved value has
    to be carried explicitly rather than re-derived.
    """
    for pty, expand, expected in [(True, None, True), (True, False, False)]:
        options = {'pty': pty} if expand is None else {'pty': pty, 'expand_keys': expand}
        dumped = ShellCommand(type='shell', cmd='x', **options).model_dump(exclude_none=True)
        assert ShellCommand(**dumped).expand_keys is expected


def test_background_with_session_still_rejected():
    with pytest.raises(ValidationError):
        ShellCommand(type='shell', cmd='x', pty=True, background=True, creates_session='s')


# --- executor ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_pty_gives_the_command_a_terminal(shell_executor):
    """The same command reports RESULT=no on the pipe path.

    printf assembles the marker so the terminal's echo of the command line
    cannot contain it and make the assertion pass for free.
    """
    result = await shell_executor._exec_cmd(
        pty_command("test -t 0 && printf 'RESULT=%s\\n' yes || printf 'RESULT=%s\\n' no\n")
    )
    assert 'RESULT=yes' in result.stdout
    assert result.returncode == 0


@pytest.mark.asyncio
async def test_pty_reports_the_configured_window_size(shell_executor):
    result = await shell_executor._exec_cmd(pty_command('stty size\n', pty_rows=40, pty_cols=100))
    assert '40 100' in result.stdout


@pytest.mark.asyncio
async def test_pty_session_persists_shell_state(shell_executor):
    await shell_executor._exec_cmd(pty_command('MARKER=42\n', creates_session='s'))
    result = await shell_executor._exec_cmd(pty_command('echo $MARKER\n', session='s'))
    assert '42' in result.stdout


def test_pty_expands_keys(shell_executor):
    """Asserted on the bytes sent, not on output: the terminal echoes the
    command back, so output-based assertions here prove nothing."""
    assert shell_executor.encode_cmd(pty_command('a<ESC>b<C-x>\n')) == b'a\x1bb\x18\n'
    assert shell_executor.encode_cmd(pty_command('a<ESC>b\n', expand_keys=False)) == b'a<ESC>b\n'


@pytest.mark.asyncio
async def test_pty_does_not_mutate_the_command(shell_executor):
    """The JSON audit log serialises the command after it ran, and Looper
    re-executes the same object - so cmd must still hold what was written."""
    command = pty_command('echo <ESC>done\n')
    await shell_executor._exec_cmd(command)
    assert command.cmd == 'echo <ESC>done\n'


def test_pty_bin_mode_is_not_key_expanded(shell_executor):
    """Hex mode carries raw bytes; expanding keys over it would corrupt them."""
    assert shell_executor.encode_cmd(pty_command('6563686f2069640a', bin=True)) == b'echo id\n'


@pytest.mark.asyncio
async def test_dead_pty_session_reports_clearly(shell_executor):
    """Without this check the failure surfaces as a confusing write error.

    _exec_cmd raises; BaseExecutor.exec is what turns an ExecException into a
    Result for the playbook.
    """
    await shell_executor._exec_cmd(pty_command('echo alive\n', creates_session='dead'))
    shell_executor.session_store.get_pty_by_session('dead').close()

    with pytest.raises(ExecException, match='has exited'):
        await shell_executor._exec_cmd(pty_command('echo again\n', session='dead'))


@pytest.mark.asyncio
async def test_screen_mode_renders_the_screen(shell_executor):
    result = await shell_executor._exec_cmd(
        pty_command('printf "\\033[2J\\033[Hclean\\n"\n', screen=True, pty_rows=10, pty_cols=40)
    )
    assert 'clean' in result.stdout
    # The screen is rendered, not the byte stream, so no escape text survives.
    assert '[2J' not in result.stdout


@pytest.mark.asyncio
async def test_read_false_returns_immediately(shell_executor):
    result = await shell_executor._exec_cmd(pty_command('echo ignored\n', read=False))
    assert result.stdout == ''


@pytest.mark.asyncio
async def test_windows_is_refused_rather_than_crashing(shell_executor, monkeypatch):
    monkeypatch.setattr(
        'attackmate.executors.shell.shellexecutor.platform.system', lambda: 'Windows'
    )
    result = await shell_executor._exec_cmd(pty_command('echo x\n'))
    assert result.returncode == 1
    assert 'Unix' in result.stdout


@pytest.mark.asyncio
async def test_pipe_path_is_unaffected(shell_executor):
    """No pty means the original behaviour, including no key expansion."""
    command = ShellCommand(type='shell', cmd='echo id')
    assert command.pty is False
    assert command.expand_keys is False
    result = await shell_executor._exec_cmd(command)
    assert result.stdout == 'id\n'


@pytest.mark.asyncio
async def test_cleanup_closes_pty_sessions(shell_executor):
    await shell_executor._exec_cmd(pty_command('echo x\n', creates_session='s'))
    session = shell_executor.session_store.get_pty_by_session('s')

    shell_executor.cleanup()

    assert shell_executor.session_store.pty_store == {}
    assert not session.is_alive()


# --- pickling ---------------------------------------------------------------


def test_pty_store_is_dropped_when_pickled():
    """A pty session owns a file descriptor and a Popen, so it cannot survive
    the pickling that dispatching a background command performs."""
    store = SessionStore()
    pty_session = PtySession('/bin/sh')
    try:
        store.set_pty_session('pty', pty_session)

        restored = pickle.loads(pickle.dumps(store))

        # Emptied, not None: a lookup in the child must raise KeyError (which
        # becomes an ExecException) rather than a TypeError on None.
        assert restored.pty_store == {}
        with pytest.raises(KeyError):
            restored.get_pty_by_session('pty')
    finally:
        pty_session.close()


def test_executor_pickles_with_a_live_session():
    executor = ShellExecutor(ProcessManager(), VariableStore())
    pty_session = PtySession('/bin/sh')
    try:
        executor.session_store.set_pty_session('s', pty_session)
        assert pickle.loads(pickle.dumps(executor)).session_store.pty_store == {}
    finally:
        pty_session.close()
