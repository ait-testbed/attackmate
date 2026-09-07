import os

import pytest

from attackmate.execexception import ExecException
from attackmate.executors.common.terminal import strip_ansi
from attackmate.executors.shell.ptysession import PtySession

pytestmark = pytest.mark.skipif(os.name != 'posix', reason='pty requires a Unix-like OS')

PROMPTS = ['# ', '$ ']


@pytest.fixture
def session():
    """A real shell behind a real pty. Closed even when the test fails."""
    pty_session = PtySession('/bin/sh', rows=30, cols=100)
    try:
        yield pty_session
    finally:
        pty_session.close()


def run(session, cmd: str, timeout: float = 5) -> str:
    session.write(cmd.encode())
    return strip_ansi(session.read(idle_timeout=timeout, prompts=PROMPTS).decode(errors='replace'))


def test_stdin_is_a_terminal(session):
    """The whole point: on the pipe path this reports RESULT=no.

    The marker is assembled by printf so that the terminal's echo of the
    command cannot contain it - otherwise the assertion would pass on any
    output at all.
    """
    output = run(session, "test -t 0 && printf 'RESULT=%s\\n' yes || printf 'RESULT=%s\\n' no\n")
    assert 'RESULT=yes' in output


def test_controlling_terminal_exists(session):
    """/dev/tty is what sudo, su and ssh read a password from.

    openpty() alone does not provide it; the TIOCSCTTY call in
    PtySession._make_controlling_terminal does.
    """
    output = run(
        session,
        "echo hi > /dev/tty 2>&1 && printf 'CTTY=%s\\n' ok || printf 'CTTY=%s\\n' fail\n",
    )
    assert 'CTTY=ok' in output


def test_window_size_is_reported(session):
    """Full-screen programs lay themselves out according to this."""
    assert '30 100' in run(session, 'stty size\n')


def test_term_is_exported(session):
    assert 'xterm-256color' in run(session, 'printf "%s\\n" "$TERM"\n')


def test_session_keeps_state_between_reads(session):
    """One shell process, so shell state persists - unlike the stateless path."""
    run(session, 'MARKER=42\n')
    assert '42' in run(session, 'echo $MARKER\n')


def test_prompt_stops_read_before_the_timeout(session):
    """A generous idle timeout must not delay a command that already finished."""
    session.write(b'echo quick\n')
    output = session.read(idle_timeout=30, prompts=PROMPTS)
    assert b'quick' in output


def test_zero_timeout_without_prompts_is_rejected(session):
    """command_timeout 0 means 'wait for a prompt', which needs prompts."""
    with pytest.raises(ExecException, match='prompts'):
        session.read(idle_timeout=0, prompts=[])


def test_zero_timeout_stops_on_prompt(session):
    session.write(b'echo unbounded\n')
    assert b'unbounded' in session.read(idle_timeout=0, prompts=PROMPTS)


def test_max_wait_caps_endless_output(session):
    """A command that never goes quiet must still return."""
    session.write(b'while true; do echo spam; done\n')
    assert session.read(idle_timeout=30, prompts=[], max_wait=1)


def test_non_utf8_output_does_not_raise(session):
    """/bin/sh printf has no \\xHH, so the octal escape is the portable one."""
    assert 'ok' in run(session, "printf 'ok\\311done\\n'\n")


def test_screen_mode_renders_the_visible_screen():
    """No editor needed: an explicit clear-and-home is the same mechanism."""
    pty_session = PtySession('/bin/sh', rows=10, cols=40, screen=True)
    try:
        pty_session.write(b'printf "\\033[2J\\033[Hclean\\n"\n')
        pty_session.read(idle_timeout=3, prompts=PROMPTS)
        assert any('clean' in line for line in pty_session.screen.display())
    finally:
        pty_session.close()


def test_close_terminates_the_shell():
    pty_session = PtySession('/bin/sh')
    assert pty_session.is_alive()
    pty_session.close()
    assert not pty_session.is_alive()
    with pytest.raises(ExecException, match='closed pty session'):
        pty_session.write(b'echo late\n')


def test_close_is_idempotent():
    """cleanup() may run after a session was already closed."""
    pty_session = PtySession('/bin/sh')
    pty_session.close()
    pty_session.close()
