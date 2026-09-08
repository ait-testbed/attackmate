import logging
import os
import socket
import subprocess
import time

import pytest

from attackmate.attackmate import AttackMate
from attackmate.executors.shell.shellexecutor import ShellExecutor
from attackmate.processmanager import ProcessManager
from attackmate.schemas.shell import ShellCommand
from attackmate.variablestore import VariableStore

pytestmark = pytest.mark.skipif(os.name != 'posix', reason='process groups require a Unix-like OS')

PROMPTS = ['# ', '$ ']


def port_is_taken(port: int) -> bool:
    probe = socket.socket()
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind(('127.0.0.1', port))
        return False
    except OSError:
        return True
    finally:
        probe.close()


@pytest.fixture
def free_port():
    holder = socket.socket()
    holder.bind(('127.0.0.1', 0))
    port = holder.getsockname()[1]
    holder.close()
    return port


@pytest.fixture
def shell_executor():
    executor = ShellExecutor(ProcessManager(), VariableStore())
    try:
        yield executor
    finally:
        executor.cleanup()


@pytest.mark.asyncio
async def test_pipe_session_does_not_outlive_the_run(shell_executor, free_port):
    """A session's listener must not survive cleanup and hold its port.

    An orphan here is worse than a crash: the next run's listener cannot bind,
    its reverse shell never connects, and every following step is still
    recorded as a success. One run silently corrupts the next.

    Closing the shell is not enough - the listener is its child and outlives
    it, which is why the whole process group has to be signalled.
    """
    await shell_executor._exec_cmd(
        ShellCommand(
            type='shell',
            cmd=f'nc -l -p {free_port} &\n',
            interactive=True,
            creates_session='listener',
            command_timeout=2,
        )
    )
    time.sleep(1)
    assert port_is_taken(free_port), 'listener never came up, so the test proves nothing'

    shell_executor.cleanup()
    time.sleep(1)

    assert not port_is_taken(free_port)
    assert shell_executor.session_store.store == {}


@pytest.mark.asyncio
async def test_pipe_session_gets_its_own_process_group(shell_executor):
    """Signalling the group is only safe once the session leads its own.

    Without start_new_session the session shares AttackMate's process group,
    and terminating it would take AttackMate down with it.
    """
    await shell_executor._exec_cmd(
        ShellCommand(
            type='shell', cmd='echo hi\n', interactive=True,
            creates_session='grouped', command_timeout=2,
        )
    )
    proc = shell_executor.session_store.get_handle_by_session('grouped')

    assert os.getpgid(proc.pid) != os.getpgid(0)
    assert os.getpgid(proc.pid) == proc.pid, 'the session shell should lead its group'


@pytest.mark.asyncio
async def test_ordinary_command_keeps_the_parent_process_group(shell_executor, monkeypatch):
    """Only sessions are detached; a plain command still shares our group, so a
    Ctrl-C at the terminal reaches it as before."""
    captured = {}
    real_popen = subprocess.Popen

    def spy(*args, **kwargs):
        captured.update(kwargs)
        return real_popen(*args, **kwargs)

    monkeypatch.setattr(subprocess, 'Popen', spy)
    await shell_executor._exec_cmd(ShellCommand(type='shell', cmd='echo plain'))

    assert captured.get('start_new_session') is False


@pytest.mark.asyncio
async def test_cleanup_runs_even_when_the_run_fails(monkeypatch, free_port):
    """Cleanup lives in a finally, so it happens however the run ends.

    exit_on_error, error_if and the loop conditions all end a run with
    exit(1). The resulting SystemExit is neither an Exception nor a
    KeyboardInterrupt, so it used to pass straight through main() and skip
    teardown entirely - leaving a live session on the target.
    """
    attackmate = AttackMate.__new__(AttackMate)
    attackmate.logger = logging.getLogger('playbook')
    attackmate.pm = ProcessManager()
    attackmate.executors = {}
    attackmate.playbook = type('PB', (), {'commands': []})()

    cleaned = {'sessions': False, 'processes': False}

    async def fake_clean():
        cleaned['sessions'] = True

    monkeypatch.setattr(attackmate, 'clean_session_stores', fake_clean)
    monkeypatch.setattr(
        attackmate.pm, 'kill_or_wait_processes',
        lambda: cleaned.__setitem__('processes', True)
    )

    async def boom(_commands):
        raise SystemExit(1)

    monkeypatch.setattr(attackmate, '_run_commands', boom)

    with pytest.raises(SystemExit):
        await attackmate.main()

    assert cleaned['sessions'], 'session stores were not cleaned on SystemExit'
    assert cleaned['processes'], 'background processes were not stopped on SystemExit'


@pytest.mark.asyncio
async def test_failing_cleanup_does_not_mask_the_original_failure(monkeypatch):
    attackmate = AttackMate.__new__(AttackMate)
    attackmate.logger = logging.getLogger('playbook')
    attackmate.pm = ProcessManager()
    attackmate.executors = {}
    attackmate.playbook = type('PB', (), {'commands': []})()

    async def broken_clean():
        raise RuntimeError('teardown exploded')

    monkeypatch.setattr(attackmate, 'clean_session_stores', broken_clean)
    monkeypatch.setattr(attackmate.pm, 'kill_or_wait_processes', lambda: None)

    async def boom(_commands):
        raise ValueError('the real failure')

    monkeypatch.setattr(attackmate, '_run_commands', boom)

    with pytest.raises(ValueError, match='the real failure'):
        await attackmate.main()
