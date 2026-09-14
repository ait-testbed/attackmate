"""
terminal.py
============================================
Helpers shared by every executor that drives a program through a real
terminal (pseudo-terminal for ``shell``, SSH channel for ``ssh``).

Three concerns live here:

* :func:`expand_keys` turns readable key names such as ``<ESC>`` or ``<C-x>``
  into the raw bytes a terminal application expects.
* :func:`strip_ansi` removes escape sequences so command output stays usable
  for logging, ``error_if`` matching and ``save``.
* :class:`TerminalScreen` renders an output stream the way a terminal would,
  which is the only way to get meaningful text out of full-screen
  applications such as ``vim`` or ``nano``.
"""

import re
import uuid
from typing import List, Optional

from attackmate.execexception import ExecException

# CSI sequences (\x1b[ ... final byte), OSC sequences (\x1b] ... BEL or ST),
# character-set selection (\x1b( etc.) and the remaining two-byte escapes.
ANSI_PATTERN = re.compile(
    r"""
    \x1b\[ [0-?]* [ -/]* [@-~]      # CSI
    | \x1b\] .*? (?: \x07 | \x1b\\ )  # OSC, terminated by BEL or ST
    | \x1b [PX^_] .*? (?: \x1b\\ )    # DCS / SOS / PM / APC
    | \x1b [()#%] .                   # charset selection
    | \x1b [@-Z\\-_]                  # remaining two-byte escapes
    | \x1b [0-?]                      # private two-byte escapes: ESC =, ESC >, ESC 7/8
    """,
    re.VERBOSE | re.DOTALL,
)

# Control characters that carry no meaning once the escape sequences are gone
# and the cursor movements below have been applied. Tab and newline are kept.
CONTROL_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

# Only the tail of a stream can end with a prompt. Re-scanning the whole
# accumulated buffer on every chunk would be quadratic on a noisy command.
PROMPT_TAIL = 512

KEY_PATTERN = re.compile(r'<([A-Za-z0-9_+-]{1,8})>')

# Key names are matched case-insensitively, so store them upper case.
NAMED_KEYS = {
    'ESC': '\x1b',
    'TAB': '\t',
    'CR': '\r',
    'LF': '\n',
    'ENTER': '\r',
    'RETURN': '\r',
    'BS': '\x08',
    'BACKSPACE': '\x7f',
    'DEL': '\x7f',
    'DELETE': '\x1b[3~',
    'SPACE': ' ',
    'NUL': '\x00',
    'UP': '\x1b[A',
    'DOWN': '\x1b[B',
    'RIGHT': '\x1b[C',
    'LEFT': '\x1b[D',
    'HOME': '\x1b[H',
    'END': '\x1b[F',
    'PGUP': '\x1b[5~',
    'PGDN': '\x1b[6~',
    'INS': '\x1b[2~',
    'F1': '\x1bOP',
    'F2': '\x1bOQ',
    'F3': '\x1bOR',
    'F4': '\x1bOS',
    'F5': '\x1b[15~',
    'F6': '\x1b[17~',
    'F7': '\x1b[18~',
    'F8': '\x1b[19~',
    'F9': '\x1b[20~',
    'F10': '\x1b[21~',
    'F11': '\x1b[23~',
    'F12': '\x1b[24~',
    # Escape hatch: <LT> produces a literal "<" so text containing key-like
    # markup can still be typed while key expansion is enabled.
    'LT': '<',
    'GT': '>',
}

CTRL_PATTERN = re.compile(r'^C-(.)$', re.IGNORECASE)


def expand_keys(text: str) -> str:
    """Replace ``<KEYNAME>`` markers in *text* with the bytes a terminal sends.

    Recognised are the names in :data:`NAMED_KEYS` and ``<C-x>`` for any
    control character. Unknown markers are left untouched, so ordinary text
    that happens to contain angle brackets survives unchanged.

    Parameters
    ----------
    text : str
        Command text as written in the playbook.

    Returns
    -------
    str
        Text with every recognised key marker replaced.
    """

    def replace(match: re.Match) -> str:
        name = match.group(1)
        if name.upper() in NAMED_KEYS:
            return NAMED_KEYS[name.upper()]
        ctrl = CTRL_PATTERN.match(name)
        if ctrl:
            char = ctrl.group(1).upper()
            # Ctrl maps @ A-Z [ \ ] ^ _ onto 0x00-0x1f.
            if '@' <= char <= '_':
                return chr(ord(char) - 0x40)
        return match.group(0)

    return KEY_PATTERN.sub(replace, text)


def apply_overwrites(text: str) -> str:
    """Resolve carriage returns and backspaces into the text they leave behind.

    A terminal does not append these, it moves the cursor: ``p\\x08printf`` is a
    shell autocompletion that reads ``printf``, and a line padded with spaces
    and followed by ``\\r`` is erased. Dropping the control characters instead
    of applying them yields text that never appeared on screen (``pprintf``),
    which then defeats ``error_if`` matching.

    Parameters
    ----------
    text : str
        Text with escape sequences already removed.

    Returns
    -------
    str
        The text as it would have ended up on screen, line by line.
    """
    lines = []
    for line in text.split('\n'):
        buffer: List[str] = []
        column = 0
        for char in line:
            if char == '\r':
                column = 0
            elif char == '\b':
                column = max(0, column - 1)
            elif column < len(buffer):
                buffer[column] = char
                column += 1
            else:
                buffer.append(char)
                column += 1
        # Deliberately not rstripped: the default prompts ('$ ', '# ', '> ')
        # all end in a space, so trimming here would stop every prompt from
        # ever matching.
        lines.append(''.join(buffer))
    return '\n'.join(lines)


def strip_ansi(text: str) -> str:
    """Remove escape sequences and resolve cursor movement in *text*.

    Terminal applications interleave their output with cursor movement and
    colour sequences. Those are noise for logging and for ``error_if``
    matching, so they are dropped, and the carriage returns and backspaces
    that remain are applied rather than deleted (see :func:`apply_overwrites`).

    Parameters
    ----------
    text : str
        Raw output as read from a terminal.

    Returns
    -------
    str
        Output containing only printable text, tabs and newlines.
    """
    text = ANSI_PATTERN.sub('', text)
    text = apply_overwrites(text)
    return CONTROL_PATTERN.sub('', text)


# Built on first use. pyte is imported lazily, so the subclass below cannot be
# declared at module level.
_SCREEN_CLASS = None


def _build_screen(pyte, rows: int, cols: int, history: int):
    """Create a pyte screen that tolerates the escape sequences real editors emit.

    ``vim`` announces its key-encoding support with a private SGR sequence
    (``\\x1b[>4;2m``). pyte 0.8.2 dispatches that to ``select_graphic_rendition``
    with a ``private`` keyword the handler does not accept, so feeding it real
    ``vim`` output raises ``TypeError`` and takes the playbook down. Private SGR
    changes no visible attribute, so dropping it loses nothing.
    """
    global _SCREEN_CLASS
    if _SCREEN_CLASS is None:

        class TolerantScreen(pyte.HistoryScreen):
            def select_graphic_rendition(self, *attrs, private=False, **kwargs):
                if private:
                    return
                super().select_graphic_rendition(*attrs)

        _SCREEN_CLASS = TolerantScreen
    return _SCREEN_CLASS(cols, rows, history=history)


class TerminalScreen:
    """A terminal emulator that turns an output stream into readable text.

    Stripping escape sequences is not enough for applications that paint the
    screen by moving the cursor around - ``nano`` and ``vim`` produce
    overlapping fragments in write order rather than what the user sees. This
    class feeds the stream through a real terminal emulator (``pyte``) and
    reports the resulting screen.

    One instance belongs to one session, so the screen keeps its state across
    commands. Output that scrolls off the top is kept in the scrollback and
    reported once, by :meth:`new_scrollback`.

    Parameters
    ----------
    rows : int
        Height of the emulated screen.
    cols : int
        Width of the emulated screen.
    history : int, optional
        Number of scrolled-off lines to retain. Defaults to ``2000``.
    """

    def __init__(self, rows: int, cols: int, history: int = 2000):
        try:
            import pyte
        except ImportError:
            raise ExecException(
                "screen mode requires the 'pyte' package. Install it with 'pip install pyte'."
            )
        self.rows = rows
        self.cols = cols
        self.screen = _build_screen(pyte, rows, cols, history)
        self.stream = pyte.ByteStream(self.screen)
        self._consumed_scrollback = 0

    def feed(self, data: bytes) -> None:
        """Advance the emulated terminal by *data*."""
        self.stream.feed(data)

    def resize(self, rows: int, cols: int) -> None:
        """Resize the emulated screen to *rows* x *cols*."""
        self.screen.resize(rows, cols)
        self.rows = rows
        self.cols = cols

    def _render_history_line(self, line) -> str:
        return ''.join(line[x].data for x in range(self.cols)).rstrip()

    def new_scrollback(self) -> List[str]:
        """Return the lines that scrolled off the top since the last call.

        Only lines not reported before are returned, so a command sees its own
        output rather than everything the session ever printed.
        """
        top = self.screen.history.top
        total = len(top)
        if total <= self._consumed_scrollback:
            # The scrollback was trimmed or reset; report nothing rather than
            # replaying lines that were already returned.
            self._consumed_scrollback = total
            return []
        fresh = list(top)[self._consumed_scrollback:]
        self._consumed_scrollback = total
        return [self._render_history_line(line) for line in fresh]

    def display(self) -> List[str]:
        """Return the currently visible screen with trailing blank lines removed."""
        lines = [line.rstrip() for line in self.screen.display]
        while lines and not lines[-1]:
            lines.pop()
        return lines

    def render(self, include_scrollback: bool = True) -> str:
        """Return the readable text produced since the previous call.

        Parameters
        ----------
        include_scrollback : bool, optional
            Prepend the lines that scrolled off the top. Defaults to ``True``.

        Returns
        -------
        str
            Scrollback plus visible screen, joined by newlines.
        """
        lines: List[str] = []
        if include_scrollback:
            lines.extend(self.new_scrollback())
        lines.extend(self.display())
        return '\n'.join(lines)


def render_output(
    raw: bytes,
    screen: Optional[TerminalScreen] = None,
    strip: bool = True,
) -> str:
    """Turn raw terminal bytes into the text a command should return.

    Parameters
    ----------
    raw : bytes
        Bytes read from the terminal for this command.
    screen : TerminalScreen, optional
        When given, the emulated screen is rendered instead of the raw stream.
        The caller is responsible for having fed *raw* into it already.
    strip : bool, optional
        Remove escape sequences from the raw stream. Ignored when *screen* is
        given, since a rendered screen never contains them.

    Returns
    -------
    str
        Decoded output. Undecodable bytes are replaced rather than raising,
        for the same reason as in the non-terminal paths: one bad byte must
        not end the playbook.
    """
    if screen is not None:
        return screen.render()
    text = raw.decode(errors='replace')
    return strip_ansi(text) if strip else text


def make_exit_marker() -> str:
    """A token that will not occur in ordinary command output."""
    return f'__ATTACKMATE_EXIT_{uuid.uuid4().hex[:12]}__'


def append_exit_marker(cmd: str, marker: str) -> str:
    """Append a marker that reports when a command finished, and with what.

    Inside a live session there is nothing to wait on: the shell does not exit
    between commands, so "run this and tell me when it is done" is unanswerable
    unless the command says so itself. Echoing a marker and ``$?`` after it
    supplies both the completion signal and the real exit status.

    This is the one thing here that rewrites the command, which is why it is
    opt-in - anything reproducing a report's commands verbatim should leave it
    off.
    """
    # The status comes first so the line ENDS with the marker, which is what
    # lets the marker be matched as a prompt.
    return f'{cmd.rstrip()}; echo "$?{marker}"\n'


def split_exit_marker(output: str, marker: str):
    """Split rendered output into the command's own output and its exit status.

    Returns ``(output, exit_status)``. The status is ``None`` when the marker
    never appeared, which means the read stopped before the command finished.
    """
    match = re.search(r'(\d+)' + re.escape(marker), output)
    if match is None:
        return output, None
    # Drop the marker line itself, and anything the shell echoed after it.
    cleaned = output[:match.start()].rstrip('\r\n')
    return cleaned, int(match.group(1))
