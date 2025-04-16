import pytest
from unittest.mock import patch, MagicMock
from attackmate.executors.browser.sessionstore import BrowserSessionStore, SessionThread


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
    result = thread.submit_command('visit', url='http://example.org')
    assert result == 'OK', "Expected the visit command to return 'OK'"

    # Stop the thread
    thread.stop_thread()
    assert thread.stopped, 'Expected the thread to be marked as stopped'


def test_session_thread_invalid_command(mock_playwright):
    """
    Submitting an unknown command should raise an Exception.
    """
    thread = SessionThread(session_name='test_session')

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

    thread = SessionThread(session_name='test_session')
    with pytest.raises(Exception) as excinfo:
        thread.submit_command('click', selector='#missing-button')

    assert 'Element #missing-button not found!' in str(excinfo.value)

    # Clean up
    thread.stop_thread()
