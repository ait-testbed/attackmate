import pytest
from pydantic import ValidationError
from unittest.mock import patch, MagicMock
from urllib.parse import quote
from attackmate.executors.browser.sessionstore import BrowserSessionStore, SessionThread
from attackmate.executors.browser.browserexecutor import BrowserExecutor, BrowserCommand


# Minimal, stable inline HTML (no network needed)
HTML_SIMPLE = "<h1>Hello World</h1>"
HTML_WITH_LINK = """
                 <!doctype html>
                 <html>
                   <body>
                     <a id="test-link" href="#next">go</a>
                     <button id="test-button">Click</button>
                   </body>
                 </html>
                 """

DATA_URL_SIMPLE = "data:text/html," + quote(HTML_SIMPLE)
DATA_URL_WITH_LINK = "data:text/html," + quote(HTML_WITH_LINK)


@pytest.fixture
def mock_playwright():
    """
    A pytest fixture that patches sync_playwright to avoid launching a real browser.
    It yields a configurable mock.
    """
    with patch('playwright.sync_api.sync_playwright') as mock_sync_playwright:
        # Create mock for the playwright object
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        # This is how the context manager start() / stop() is called:
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright_instance
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance

        yield {
            'mock_sync_playwright': mock_sync_playwright,
            'mock_playwright_instance': mock_playwright_instance,
            'mock_browser': mock_browser,
            'mock_context': mock_context,
            'mock_page': mock_page,
        }


# ----------------------------------------------------------------------------------------
# Tests for BrowserSessionStore
# ----------------------------------------------------------------------------------------

def test_browser_session_store_creation_and_retrieval():
    store = BrowserSessionStore()
    assert not store.has_session('test_session'), "Expected store to not have 'test_session' initially"

    # Create a dummy SessionThread (not started for real in this test)
    thread = MagicMock(spec=SessionThread)
    store.set_session('test_session', thread)
    assert store.has_session('test_session'), "Expected store to have 'test_session' after setting"

    retrieved = store.get_session('test_session')
    assert retrieved is thread, 'Expected retrieved session to be the same instance stored'


def test_browser_session_store_close_session():
    store = BrowserSessionStore()
    thread = MagicMock(spec=SessionThread)
    store.set_session('test_session', thread)

    store.close_session('test_session')
    assert not store.has_session('test_session'), 'Session should have been removed after close_session'
    thread.stop_thread.assert_called_once()


def test_browser_session_store_close_all():
    store = BrowserSessionStore()
    thread1 = MagicMock(spec=SessionThread)
    thread2 = MagicMock(spec=SessionThread)

    store.set_session('session1', thread1)
    store.set_session('session2', thread2)

    store.close_all()
    assert not store.has_session('session1')
    assert not store.has_session('session2')
    thread1.stop_thread.assert_called_once()
    thread2.stop_thread.assert_called_once()


# ----------------------------------------------------------------------------------------
# Tests for SessionThread
# ----------------------------------------------------------------------------------------

def test_session_thread_lifecycle(mock_playwright):
    """
    Tests that the SessionThread starts and stops without error,
    and that commands can be submitted.
    """
    thread = SessionThread(session_name='test_session', headless=True)

    # Submit a command. This should go onto the queue, be processed, and return 'OK'
    result = thread.submit_command('visit', url=DATA_URL_SIMPLE)
    assert result == 'OK', "Expected the visit command to return 'OK'"

    # Stop the thread
    thread.stop_thread()
    assert thread.stopped, 'Expected the thread to be marked as stopped'


def test_session_thread_invalid_command(mock_playwright):
    """
    Submitting an unknown command should raise an Exception.
    """
    thread = SessionThread(session_name='test_session', headless=True)

    with pytest.raises(Exception) as excinfo:
        thread.submit_command('non_existent_command')

    assert 'Unknown command: non_existent_command' in str(excinfo.value)

    # Clean up
    thread.stop_thread()


def test_session_thread_click_selector_not_found(mock_playwright):
    """
    Submitting a click command for a missing selector should raise an Exception.
    """
    # Make the mock page return None for query_selector => simulates "element not found"
    mock_page = mock_playwright['mock_page']
    mock_page.query_selector.return_value = None

    thread = SessionThread(session_name='test_session', headless=True)
    with pytest.raises(Exception) as excinfo:
        thread.submit_command('click', selector='#missing-button')

    assert 'Locator.wait_for: Timeout 10000ms exceeded' in str(excinfo.value)

    # Clean up
    thread.stop_thread()


# ----------------------------------------------------------------------------------------
# Tests for BrowserExecutor
# ----------------------------------------------------------------------------------------

@pytest.fixture
def browser_executor(mock_playwright):
    """
    Provides a mocked BrowserExecutor instance
    """
    return BrowserExecutor(pm=None, varstore=None)


def test_browser_executor_ephemeral_session(browser_executor):
    """
    Tests that an ephemeral session is created and destroyed when no session is specified.
    """
    command = BrowserCommand(
        type='browser',
        cmd='visit',
        url=DATA_URL_SIMPLE,
        headless=True
    )
    result = browser_executor._exec_cmd(command)
    assert result.returncode == 0
    assert 'Browser command executed successfully.' in result.stdout


def test_browser_executor_named_session(browser_executor):
    """
    Tests that a named session is created and remains available, then can be reused.
    """
    create_cmd = BrowserCommand(
        type='browser',
        cmd='visit',
        url=DATA_URL_WITH_LINK,
        creates_session='my_session',
        headless=True
    )
    result1 = browser_executor._exec_cmd(create_cmd)
    assert result1.returncode == 0
    assert 'executed successfully' in result1.stdout

    # Now reuse the same session
    reuse_cmd = BrowserCommand(
        type='browser',
        cmd='click',
        selector='#test-link',  # matches the anchor in DATA_URL_WITH_LINK
        session='my_session'
    )
    result2 = browser_executor._exec_cmd(reuse_cmd)
    assert result2.returncode == 0
    assert 'executed successfully' in result2.stdout


def test_browser_executor_no_such_session(browser_executor):
    """
    If we specify a session that doesn't exist, we should get an error result.
    """
    bad_cmd = BrowserCommand(
        type='browser',
        cmd='click',
        selector='#some-button',
        session='nonexistent_session'
    )
    result = browser_executor._exec_cmd(bad_cmd)
    assert result.returncode == 1
    assert "Session 'nonexistent_session' not found!" in result.stdout


def test_browser_executor_recreate_same_session(browser_executor):
    """
    If we specify creates_session with the same name again,
    it should close the old one and create a fresh session.
    """
    cmd1 = BrowserCommand(
        type='browser',
        cmd='visit',
        url=DATA_URL_SIMPLE,
        creates_session='my_session',
        headless=True
    )
    res1 = browser_executor._exec_cmd(cmd1)
    assert res1.returncode == 0

    cmd2 = BrowserCommand(
        type='browser',
        cmd='visit',
        url=DATA_URL_WITH_LINK,
        creates_session='my_session',
        headless=True
    )
    # This should close the old 'my_session' and create a new one
    res2 = browser_executor._exec_cmd(cmd2)
    assert res2.returncode == 0
    assert 'executed successfully' in res2.stdout


def test_browser_executor_unknown_command_validation():
    """
    Any cmd outside {'visit','click','type','screenshot'}
    is rejected by BrowserCommand’s Literal validator.
    """
    with pytest.raises(ValidationError):
        BrowserCommand(
            type='browser',
            cmd='zoom',  # invalid literal, should be one of [visit, click, type, screenshot]
            url=DATA_URL_SIMPLE
        )
