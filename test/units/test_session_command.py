import os

import pytest
from pydantic import ValidationError

from attackmate.attackmate import AttackMate
from attackmate.executors.common.terminal import (append_exit_marker, make_exit_marker,
                                                  split_exit_marker)
from attackmate.executors.shell.shellexecutor import ShellExecutor
from attackmate.processmanager import ProcessManager
from attackmate.schemas.playbook import Playbook
from attackmate.schemas.session import SessionCommand
from attackmate.schemas.shell import ShellCommand
from attackmate.variablestore import VariableStore

pytestmark = pytest.mark.skipif(os.name != 'posix', reason='spawns real shells')

PROMPTS = ['# ', '$ ']


@pytest.fixture
def shell_executor():
    executor = ShellExecutor(ProcessManager(), VariableStore())
    try:
        yield executor
    finally:
        executor.cleanup()


# --- wait_for_exit and read_timeout ----------------------------------------


def test_marker_terminates_the_line_so_it_can_be_matched():
    """The status has to come before the marker. With the marker first the line
    ends in digits, and nothing that matches on a trailing token can see it."""
    marker = make_exit_marker()
    sent = append_exit_marker('./scan.sh', marker)
    assert sent.rstrip().endswith(f'{marker}"')


def test_split_exit_marker_extracts_status_and_removes_the_marker():
    marker = make_exit_marker()
    output, status = split_exit_marker(f'real output\r\n42{marker}\r\n', marker)
    assert output == 'real output'
    assert status == 42


def test_split_exit_marker_reports_none_before_the_command_finished():
    """No marker yet means the read stopped early, not that it succeeded."""
    assert split_exit_marker('partial', make_exit_marker()) == ('partial', None)


def test_wait_for_exit_is_rejected_in_bin_mode():
    """bin mode sends raw bytes, which cannot carry an appended marker."""
    with pytest.raises(ValidationError, match='bin mode'):
        ShellCommand(type='shell', cmd='6964', bin=True, wait_for_exit=True)


@pytest.mark.asyncio
async def test_wait_for_exit_waits_for_completion_and_reports_the_status(shell_executor):
    """command_timeout is an idle timeout, so a script that prints nothing for
    a while looks finished when it is not. This is the linpeas case."""
    command = ShellCommand(
        type='shell', pty=True, creates_session='w',
        cmd='sleep 3; echo SCRIPT_DONE; (exit 3)',
        command_timeout=1, wait_for_exit=True,
    )
    result = await shell_executor._exec_cmd(command)

    assert 'SCRIPT_DONE' in result.stdout
    assert result.exit_status == 3
    # The marker itself must not survive into the recorded output.
    assert '__ATTACKMATE_EXIT_' not in result.stdout


@pytest.mark.asyncio
async def test_idle_timeout_alone_returns_before_the_command_finished(shell_executor):
    """The behaviour wait_for_exit exists to fix."""
    result = await shell_executor._exec_cmd(
        ShellCommand(type='shell', pty=True, creates_session='i',
                     cmd='sleep 3; echo SCRIPT_DONE\n', command_timeout=1)
    )
    assert 'SCRIPT_DONE' not in result.stdout


@pytest.mark.asyncio
async def test_read_timeout_bounds_a_command_that_never_goes_quiet(shell_executor):
    """The idle timeout cannot end a command that keeps producing output."""
    result = await shell_executor._exec_cmd(
        ShellCommand(type='shell', pty=True, creates_session='r',
                     cmd='while true; do echo spam; done\n',
                     command_timeout=30, read_timeout=2)
    )
    assert 'spam' in result.stdout


# --- the session command ----------------------------------------------------


@pytest.fixture
def attackmate_with_session():
    attackmate = AttackMate(playbook=Playbook(commands=[], vars={}))
    try:
        yield attackmate
    finally:
        for executor in attackmate.executors.values():
            if hasattr(executor, 'cleanup'):
                executor.cleanup()


async def open_shell_session(attackmate, name='foothold'):
    await attackmate.run_command(
        ShellCommand(type='shell', cmd='echo alive\n', interactive=True,
                     creates_session=name, command_timeout=2)
    )


@pytest.mark.asyncio
async def test_status_reports_a_live_session(attackmate_with_session):
    await open_shell_session(attackmate_with_session)
    result = await attackmate_with_session.run_command(
        SessionCommand(type='session', cmd='status', session='foothold')
    )
    assert result.returncode == 0
    assert 'is alive' in result.stdout


@pytest.mark.asyncio
async def test_close_ends_a_session_early(attackmate_with_session):
    """Sessions used to live until the end of the run with no way to close one."""
    await open_shell_session(attackmate_with_session)
    result = await attackmate_with_session.run_command(
        SessionCommand(type='session', cmd='close', session='foothold')
    )

    assert result.returncode == 0
    store = attackmate_with_session.executors['shell'].session_store
    assert not store.session_exists('foothold')


@pytest.mark.asyncio
async def test_status_after_close_reports_it_is_gone(attackmate_with_session):
    await open_shell_session(attackmate_with_session)
    await attackmate_with_session.run_command(
        SessionCommand(type='session', cmd='close', session='foothold')
    )
    result = await attackmate_with_session.run_command(
        SessionCommand(type='session', cmd='status', session='foothold', exit_on_error=False)
    )
    assert result.returncode == 1


@pytest.mark.asyncio
async def test_unknown_session_fails_without_ending_the_run(attackmate_with_session):
    """An executor that has never run has no sessions, rather than no store."""
    result = await attackmate_with_session.run_command(
        SessionCommand(type='session', cmd='close', session='nope',
                       executor='ssh', exit_on_error=False)
    )
    assert result.returncode == 1
    assert 'does not exist' in result.stdout


@pytest.mark.asyncio
async def test_closing_a_pty_session_also_works(attackmate_with_session):
    """The shell store holds two kinds of session and both must be reachable."""
    await attackmate_with_session.run_command(
        ShellCommand(type='shell', cmd='echo alive\n', pty=True,
                     creates_session='ptysess', command_timeout=2, prompts=PROMPTS)
    )
    result = await attackmate_with_session.run_command(
        SessionCommand(type='session', cmd='close', session='ptysess')
    )

    assert result.returncode == 0
    assert not attackmate_with_session.executors['shell'].session_store.session_exists('ptysess')


# --- environment overrides --------------------------------------------------


def test_env_override_reports_what_it_replaced(monkeypatch):
    """The playbook on disk otherwise does not fully determine what ran, and
    nothing recorded the difference."""
    monkeypatch.setenv('ATTACKMATE_TARGET', 'from_environment')
    store = VariableStore()
    store.from_dict({'$TARGET': 'from_playbook', '$OTHER': 'untouched'})

    replaced = store.replace_with_prefixed_env_vars()

    assert replaced == ['TARGET']
    assert store.get_variable('TARGET') == 'from_environment'
    assert store.get_variable('OTHER') == 'untouched'


def test_env_override_reports_nothing_when_it_changed_nothing():
    assert VariableStore().replace_with_prefixed_env_vars() == []


# --- wait_for_exit on a pipe-based session ----------------------------------


@pytest.mark.asyncio
async def test_wait_for_exit_works_without_a_pty(shell_executor):
    """The pipe path needs the marker as much as the pty one does. Its idle
    timeout has the same blind spot: a command that pauses looks finished."""
    result = await shell_executor._exec_cmd(
        ShellCommand(type='shell', interactive=True, creates_session='pipe',
                     cmd='sleep 3; echo PIPE_DONE; (exit 9)',
                     command_timeout=1, wait_for_exit=True)
    )

    assert 'PIPE_DONE' in result.stdout
    assert result.exit_status == 9
    assert '__ATTACKMATE_EXIT_' not in result.stdout


@pytest.mark.asyncio
async def test_pipe_idle_timeout_alone_still_returns_early(shell_executor):
    result = await shell_executor._exec_cmd(
        ShellCommand(type='shell', interactive=True, creates_session='pipeidle',
                     cmd='sleep 3; echo PIPE_DONE\n', command_timeout=1)
    )
    assert 'PIPE_DONE' not in result.stdout


@pytest.mark.asyncio
async def test_read_timeout_bounds_the_pipe_path_too(shell_executor):
    result = await shell_executor._exec_cmd(
        ShellCommand(type='shell', interactive=True, creates_session='pipespam',
                     cmd='while true; do echo spam; done\n',
                     command_timeout=30, read_timeout=2)
    )
    assert 'spam' in result.stdout


@pytest.mark.asyncio
async def test_wait_for_exit_gives_up_when_the_session_dies(shell_executor):
    """Waiting for a marker that can never arrive must not hang the run."""
    result = await shell_executor._exec_cmd(
        ShellCommand(type='shell', interactive=True,
                     cmd='exit 5', command_timeout=1, wait_for_exit=True)
    )
    # The shell exited before echoing the marker, so there is no status to report.
    assert result.exit_status is None


@pytest.mark.asyncio
async def test_non_interactive_command_gets_no_marker(shell_executor):
    """It is run to completion anyway and already reports a real status, so
    rewriting the command there would buy nothing."""
    result = await shell_executor._exec_cmd(
        ShellCommand(type='shell', cmd="sh -c 'exit 4'", wait_for_exit=True)
    )
    assert result.exit_status == 4
    assert '__ATTACKMATE_EXIT_' not in result.stdout
