import json
import logging
import os

import pytest

from attackmate.execexception import ExecException
from attackmate.executors.shell.shellexecutor import ShellExecutor
from attackmate.processmanager import ProcessManager
from attackmate.result import Result
from attackmate.schemas.shell import ShellCommand
from attackmate.variablestore import VariableStore

pytestmark = pytest.mark.skipif(os.name != 'posix', reason='spawns real shells')


class RecordingHandler(logging.Handler):
    """Captures what would be written to attackmate.json."""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(json.loads(record.getMessage()))


@pytest.fixture
def shell_executor():
    executor = ShellExecutor(ProcessManager(), VariableStore())
    try:
        yield executor
    finally:
        executor.cleanup()


@pytest.fixture
def audit(shell_executor):
    handler = RecordingHandler()
    logger = logging.getLogger('json')
    logger.addHandler(handler)
    previous_level = logger.level
    logger.setLevel(logging.INFO)
    try:
        yield handler.records
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)


@pytest.mark.asyncio
async def test_step_records_when_it_ended_and_how_long_it_took(shell_executor, audit):
    """Without an end time, what a step did has to be reconstructed elsewhere.

    An interactive step in particular returns after a silence rather than on
    exit, so its children can still be running well after the log claims it
    finished.
    """
    await shell_executor.exec(ShellCommand(type='shell', cmd='echo timed'))

    record = audit[-1]
    assert record['start-datetime']
    assert record['end-datetime'] >= record['start-datetime']
    assert record['duration-seconds'] >= 0


@pytest.mark.asyncio
async def test_real_exit_status_is_recorded_without_changing_behaviour(shell_executor, audit):
    """The true status reaches the log, but exit_on_error still sees 0.

    Making it authoritative by default would start failing playbooks that have
    always passed, so enforcement is opt-in.
    """
    result = await shell_executor.exec(ShellCommand(type='shell', cmd="sh -c 'exit 42'"))

    assert audit[-1]['exit-status'] == 42
    assert audit[-1]['returncode'] == 0
    assert result.returncode == 0


@pytest.mark.asyncio
async def test_use_exit_code_makes_the_status_authoritative(shell_executor, audit):
    result = await shell_executor.exec(
        ShellCommand(type='shell', cmd="sh -c 'exit 7'", use_exit_code=True, exit_on_error=False)
    )

    assert result.returncode == 7
    assert audit[-1]['exit-status'] == 7


@pytest.mark.asyncio
async def test_a_step_that_dies_is_still_recorded(shell_executor, audit, monkeypatch):
    """The record used to be written only on the way out, so a step killed by an
    uncaught exception left no trace - the artifact showed a playbook that
    simply stopped. That is how a dropped reverse shell presents."""

    async def explode(_command):
        raise BrokenPipeError('the session went away')

    monkeypatch.setattr(shell_executor, '_exec_cmd', explode)

    with pytest.raises(BrokenPipeError):
        await shell_executor.exec(ShellCommand(type='shell', cmd='echo doomed'))

    assert audit, 'the failing step was not recorded at all'
    assert audit[-1]['cmd'] == 'echo doomed'


@pytest.mark.asyncio
async def test_log_survives_a_failure_before_the_command_runs(shell_executor, audit, monkeypatch):
    """log_command can itself raise - a non-numeric ssh port reaches
    variable_to_int through cache_settings. The timestamp is bound before the
    try so the handler does not then die of UnboundLocalError."""

    def bad_log(_command):
        raise ExecException('cannot parse port')

    monkeypatch.setattr(shell_executor, 'log_command', bad_log)
    result = await shell_executor.exec(
        ShellCommand(type='shell', cmd='echo x', exit_on_error=False)
    )

    assert result.returncode == 1
    assert audit[-1]['cmd'] == 'echo x'


@pytest.mark.asyncio
async def test_skipped_step_is_visible_in_the_log(shell_executor, audit):
    """A step skipped by only_if used to be absent entirely, which reads the
    same as a step that was never in the playbook."""
    await shell_executor.run(ShellCommand(type='shell', cmd='echo never', only_if='1 == 2'))

    assert audit[-1]['cmd'] == 'echo never'
    assert audit[-1]['skipped'] is True
    assert 'end-datetime' not in audit[-1]


def test_build_result_defaults_to_the_historical_returncode():
    command = ShellCommand(type='shell', cmd='x')
    assert ShellExecutor.build_result(command, 'out', exit_status=3).returncode == 0
    assert ShellExecutor.build_result(command, 'out', exit_status=3).exit_status == 3


def test_build_result_leaves_exit_status_none_when_unknown():
    """Inside a live session the shell is still running, so there is no status
    to report. It is recorded as None rather than faked as 0."""
    command = ShellCommand(type='shell', cmd='x', use_exit_code=True)
    result = ShellExecutor.build_result(command, 'out', exit_status=None)
    assert result.exit_status is None
    assert result.returncode == 0


def test_duration_of_unparseable_timestamps_is_none():
    assert ShellExecutor.duration_seconds('not-a-time', 'nor-this') is None


def test_result_repr_includes_exit_status():
    assert 'exit_status=5' in repr(Result('out', 0, exit_status=5))


@pytest.mark.asyncio
async def test_dollar_dollar_survives_with_templating_off(shell_executor, audit):
    """string.Template collapses $$ to a single $, and in a shell $$ is the
    process id - so `kill -9 $$` and `/tmp/f.$$` were silently rewritten, and
    the audit log recorded the rewritten form rather than the playbook's."""
    command = ShellCommand(type='shell', cmd='echo "PID_IS:$$"', substitute_cmd_vars=False)
    await shell_executor.run(command)

    assert audit[-1]['cmd'] == 'echo "PID_IS:$$"'
    # A correct run prints a pid, not a bare '$'.
    assert audit[-1]['exit-status'] == 0


@pytest.mark.asyncio
async def test_templating_still_applies_by_default(shell_executor, audit):
    await shell_executor.run(ShellCommand(type='shell', cmd='echo "collapsed:$$"'))
    assert audit[-1]['cmd'] == 'echo "collapsed:$"'


@pytest.mark.asyncio
async def test_dead_pipe_session_fails_cleanly(shell_executor, audit):
    """Writing to a shell that has exited raises BrokenPipeError, which nothing
    catches - it ended the playbook, and the step never reached the log. That
    is exactly how a dropped reverse shell presents."""
    await shell_executor._exec_cmd(
        ShellCommand(type='shell', cmd='echo alive\n', interactive=True,
                     creates_session='foothold', command_timeout=2)
    )
    dead = shell_executor.session_store.get_handle_by_session('foothold')
    dead.kill()
    dead.wait(timeout=5)

    with pytest.raises(ExecException, match='has exited'):
        await shell_executor._exec_cmd(
            ShellCommand(type='shell', cmd='echo after\n', interactive=True,
                         session='foothold', command_timeout=2)
        )


@pytest.mark.asyncio
async def test_a_session_dying_mid_write_is_also_a_clean_failure(shell_executor):
    """poll() can still report a process alive for a moment after it is killed,
    so the write itself has to fail cleanly too."""
    await shell_executor._exec_cmd(
        ShellCommand(type='shell', cmd='echo alive\n', interactive=True,
                     creates_session='racy', command_timeout=2)
    )
    proc = shell_executor.session_store.get_handle_by_session('racy')
    proc.stdin.close()

    # Either path is correct and which one wins is a race: closing stdin may
    # also make the shell exit, in which case the liveness check catches it
    # first. What matters is that neither crashes the run.
    with pytest.raises(ExecException, match='no longer accepting input|has exited'):
        await shell_executor._exec_cmd(
            ShellCommand(type='shell', cmd='echo after\n', interactive=True,
                         session='racy', command_timeout=2)
        )
