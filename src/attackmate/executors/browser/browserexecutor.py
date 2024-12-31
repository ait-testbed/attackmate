import time
from playwright.sync_api import sync_playwright
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.browser import BrowserCommand
from attackmate.executors.executor_factory import executor_factory
from .sessionstore import BrowserSessionStore


@executor_factory.register_executor('browser')
class BrowserExecutor(BaseExecutor):
    def __init__(self, pm, varstore, **kwargs):
        super().__init__(pm, varstore, **kwargs)
        self.session_store = BrowserSessionStore()
        self.command_delay = 2  # TODO: what's the best way to handle delay between commands?

    def log_command(self, command: BrowserCommand):
        self.logger.info(f"Executing Browser Command: {command.cmd}")

    def open_browser(self, command: BrowserCommand):
        if command.session and self.session_store.has_session(command.session):
            # Reuse existing session
            return self.session_store.get_session(command.session)

        # create a new session
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)  # TODO: make it an option to set in playbook
        context = browser.new_context()
        page = context.new_page()

        # store session if requested
        if command.creates_session:
            self.session_store.set_session(command.creates_session, browser, context, page)

        return browser, context, page

    def close_browser(self, browser=None, context=None, page=None):
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()

    def _exec_cmd(self, command: BrowserCommand) -> Result:
        browser, context, page = None, None, None
        try:
            # get or create browser, context, and page
            browser, context, page = self.open_browser(command)

            # Execute the command
            if command.cmd == 'visit':
                page.goto(command.url)
            elif command.cmd == 'click':
                page.click(command.selector)
            elif command.cmd == 'type':
                page.fill(command.selector, command.text)
            elif command.cmd == 'screenshot':
                page.screenshot(path=command.screenshot_path)
            else:
                raise ValueError(f"Unknown browser command: {command.cmd}")

            # delay for visibility
            time.sleep(self.command_delay)

            return Result('Browser command executed successfully.', 0)

        except Exception as e:
            return Result(str(e), 1)

        finally:
            # close the browser resources if not using a session
            if not command.session and not command.creates_session:
                self.close_browser(browser, context, page)
