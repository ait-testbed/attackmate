import threading
from playwright.sync_api import sync_playwright
from queue import Queue, Empty


class SessionThread(threading.Thread):
    """
    A dedicated thread that manages a single Playwright browser session (browser, context, page).
    All commands for this session are queued to make sure they run synchronously in this thread.
    """
    def __init__(self, session_name=None, headless=False):
        super().__init__()
        self.session_name = session_name
        self.headless = headless
        self.cmd_queue = Queue()
        self.res_queue = Queue()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.stopped = False
        self.daemon = True  # mark this thread as a daemon so it won’t block interpreter exit
        self.start()

    def run(self):
        """
        Main loop of the thread. It:
          1. Starts Playwright.
          2. Waits for commands on the cmd_queue.
          3. Executes them.
          4. Puts results on the res_queue.
          5. Shuts down on stop signal.
        """
        self.playwright = sync_playwright().start()

        while not self.stopped:
            try:
                command = self.cmd_queue.get(timeout=0.1)
            except Empty:
                continue

            if command is None:
                break  # signals that we're done

            cmd_name, args, kwargs = command
            try:
                result = self._handle_command(cmd_name, *args, **kwargs)
                self.res_queue.put((result, None))
            except Exception as e:
                self.res_queue.put((None, e))

        # Cleanup
        self._close_browser()
        self.playwright.stop()

    def _init_browser(self):
        """Initialize the browser/context/page if not already open."""
        if not self.browser:
            try:
                self.browser = self.playwright.chromium.launch(headless=self.headless)
                self.context = self.browser.new_context()
                self.context.set_default_timeout(10_000)  # element operations
                self.context.set_default_navigation_timeout(30_000)  # navigations
                self.page = self.context.new_page()
            except Exception:
                raise

    def _close_browser(self):
        """Close browser resources if they exist."""
        if self.page:
            self.page.close()
            self.page = None
        if self.context:
            self.context.close()
            self.context = None
        if self.browser:
            self.browser.close()
            self.browser = None

    def _handle_command(self, cmd_name, *args, **kwargs):
        """Executes the given command (visit, click, type, screenshot, etc.) in this thread."""
        # Make sure we have a browser/page:
        self._init_browser()

        if cmd_name == 'visit':
            url = kwargs['url']
            self.page.goto(url, wait_until='networkidle')
        elif cmd_name == 'click':
            selector = kwargs['selector']
            locator = self.page.locator(selector)
            locator.wait_for(state='visible', timeout=10000)
            locator.click()
        elif cmd_name == 'type':
            selector = kwargs['selector']
            text = kwargs['text']
            locator = self.page.locator(selector)
            locator.wait_for(state='visible', timeout=10000)
            locator.fill(text)
        elif cmd_name == 'screenshot':
            screenshot_path = kwargs['screenshot_path']
            self.page.screenshot(path=screenshot_path)
        else:
            raise ValueError(f"Unknown command: {cmd_name}")

        return 'OK'

    def submit_command(self, cmd_name, *args, **kwargs):
        """
        Called from outside to run a command in this thread.
        This is a synchronous call from the caller’s perspective:
         - we place the command on cmd_queue,
         - then wait for the response in res_queue
         - re-raise the exception to preserve traceback if it failed
        """
        self.cmd_queue.put((cmd_name, args, kwargs))
        result, error = self.res_queue.get()
        if error:
            raise error
        return result

    def stop_thread(self):
        """Signals the thread to stop and waits for it to join."""
        self.stopped = True
        self.cmd_queue.put(None)
        self.join()


class BrowserSessionStore:
    """
    Manages named sessions. Each named session has its own SessionThread.
    """
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    def has_session(self, session_name):
        with self.lock:
            return session_name in self.sessions

    def get_session(self, session_name):
        with self.lock:
            return self.sessions[session_name]

    def set_session(self, session_name, session_thread):
        with self.lock:
            self.sessions[session_name] = session_thread

    def close_session(self, session_name):
        with self.lock:
            if session_name in self.sessions:
                thread = self.sessions[session_name]
                thread.stop_thread()
                del self.sessions[session_name]

    def close_all(self):
        """Stop and remove all SessionThreads."""
        with self.lock:
            for name, thread in list(self.sessions.items()):
                thread.stop_thread()
                del self.sessions[name]
