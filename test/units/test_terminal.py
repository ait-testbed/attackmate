import pytest

from attackmate.executors.common.terminal import (
    TerminalScreen,
    apply_overwrites,
    expand_keys,
    render_output,
    strip_ansi,
)


@pytest.mark.parametrize(
    'text, expected',
    [
        ('<ESC>', '\x1b'),
        ('<esc>', '\x1b'),
        ('<CR>', '\r'),
        ('<TAB>', '\t'),
        ('<UP>', '\x1b[A'),
        ('<F1>', '\x1bOP'),
        ('iHello<ESC>:wq!<CR>', 'iHello\x1b:wq!\r'),
    ],
)
def test_expand_keys_named(text, expected):
    assert expand_keys(text) == expected


@pytest.mark.parametrize(
    'text, expected',
    [
        ('<C-x>', '\x18'),
        ('<C-o>', '\x0f'),
        ('<C-c>', '\x03'),
    ],
)
def test_expand_keys_control(text, expected):
    assert expand_keys(text) == expected


def test_expand_keys_leaves_unknown_markup_alone():
    """Ordinary text with angle brackets must survive key expansion."""
    assert expand_keys('a < b and c <notakey> d') == 'a < b and c <notakey> d'


def test_expand_keys_escape_hatch():
    """<LT> is how a literal '<' is typed while expansion is on."""
    assert expand_keys('<LT>ESC<GT>') == '<ESC>'


def test_expand_keys_is_not_idempotent_so_callers_must_not_mutate():
    """Guards the reason ShellExecutor.encode_cmd works on a copy.

    Looper re-executes the same command object, so expanding in place would
    turn a literal <ESC> into a real escape byte on the second pass.
    """
    once = expand_keys('<LT>ESC<GT>')
    assert once == '<ESC>'
    assert expand_keys(once) == '\x1b'


@pytest.mark.parametrize(
    'text, expected',
    [
        ('\x1b[31mred\x1b[0m', 'red'),
        ('\x1b]0;title\x07rest', 'rest'),
        ('a\r\nb', 'a\nb'),
        ('\x1b[?1049h\x1b[22;0;0thi', 'hi'),
        # ESC = and ESC > are emitted by shells around every prompt.
        ('x\x1b>y\x1b=z', 'xyz'),
        ('keep\ttab', 'keep\ttab'),
    ],
)
def test_strip_ansi(text, expected):
    assert strip_ansi(text) == expected


@pytest.mark.parametrize(
    'text, expected',
    [
        # A carriage return rewrites the line rather than adding to it.
        ('progress 10%\rprogress 99%', 'progress 99%'),
        # Shell autocompletion backspaces over what it echoed.
        ('p\x08printf', 'printf'),
        ('abc\rx', 'xbc'),
        # A bare carriage return moves the cursor but erases nothing.
        ('padded    \r', 'padded    '),
    ],
)
def test_apply_overwrites(text, expected):
    assert apply_overwrites(text) == expected


def test_strip_ansi_keeps_the_trailing_space_of_a_prompt():
    """The default prompts ('$ ', '# ', '> ') all end in a space, so trimming
    it would stop prompt matching from ever terminating a read."""
    assert strip_ansi('\x1b[32mroot@host:~# \x1b[0m').endswith('# ')


def test_render_output_strips_by_default():
    assert render_output(b'\x1b[1mbold\x1b[0m plain') == 'bold plain'


def test_render_output_can_keep_escapes():
    assert '\x1b' in render_output(b'\x1b[1mbold\x1b[0m', strip=False)


def test_render_output_replaces_undecodable_bytes():
    """One bad byte must not end the playbook, as on the non-terminal paths."""
    assert render_output(b'ok\xc9done') == 'ok�done'


def test_screen_survives_private_sgr():
    """Regression guard for the pyte 0.8.2 crash.

    vim announces its key encoding with a private SGR sequence. Stock
    pyte dispatches it as select_graphic_rendition(private=True) and raises
    TypeError, which would take the whole playbook down.
    """
    screen = TerminalScreen(rows=4, cols=30)
    screen.feed(b'\x1b[>4;2mhello \x1b[1mbold\x1b[m world')
    assert screen.display() == ['hello bold world']


def test_screen_resolves_cursor_movement():
    """What separates screen mode from plain stripping."""
    screen = TerminalScreen(rows=3, cols=10)
    screen.feed(b'aaa\rbbb')
    assert screen.display() == ['bbb']


def test_screen_reports_scrollback_only_once():
    """Each command must see its own output, not the whole session's."""
    screen = TerminalScreen(rows=4, cols=20, history=100)
    screen.feed(b''.join(f'line{i}\r\n'.encode() for i in range(20)))

    first = screen.new_scrollback()
    assert first
    assert 'line0' in first[0]
    assert screen.new_scrollback() == []
