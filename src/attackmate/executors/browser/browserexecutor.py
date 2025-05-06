from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.browser import BrowserCommand
from attackmate.executors.executor_factory import executor_factory
from .sessionstore import BrowserSessionStore, SessionThread


@executor_factory.register_executor('browser')
class BrowserExecutor(BaseExecutor):
    def __init__(self, pm, varstore, **kwargs):
        super().__init__(pm, varstore, **kwargs)
        self.session_store = BrowserSessionStore()

    def log_command(self, command: BrowserCommand):
        self.logger.info(
            f"Executing Browser Command: {command.cmd}"
            f"{f' {command.selector}' if command.selector else ''}"
            f"{f' {command.url}' if command.url else ''}"
        )

    def _exec_cmd(self, command: BrowserCommand) -> Result:
        session_thread = None
        # Determine if this should be an ephemeral session (no session name set or created)
        ephemeral = not command.session and not command.creates_session

        try:
            # Decide whether we’re using or creating a named session, or ephemeral
            if command.session:
                # We expect an existing session by this name
                if not self.session_store.has_session(command.session):
                    return Result(f"Session '{command.session}' not found!", 1)
                session_thread = self.session_store.get_session(command.session)
            elif command.creates_session:
                # before creating a new session, close if a session with the same name already exists
                if self.session_store.has_session(command.creates_session):
                    self.logger.warning(
                        f"Session '{command.creates_session}' already exists! "
                        f"Closing it before creating a new one."
                    )
                    self.session_store.close_session(command.creates_session)
                session_thread = SessionThread(
                    session_name=command.creates_session,
                    headless=command.headless or False
                )
                self.session_store.set_session(command.creates_session, session_thread)
            else:
                # No session info => ephemeral
                session_thread = SessionThread(headless=command.headless or False)

            # Execute the command
            if command.cmd == 'visit':
                session_thread.submit_command('visit', url=command.url)
            elif command.cmd == 'click':
                session_thread.submit_command('click', selector=command.selector)
            elif command.cmd == 'type':
                session_thread.submit_command('type', selector=command.selector, text=command.text)
            elif command.cmd == 'screenshot':
                session_thread.submit_command('screenshot', screenshot_path=command.screenshot_path)
            else:
                return Result(f"Unknown browser command: {command.cmd}", 1)

            return Result('Browser command executed successfully.', 0)

        except Exception as e:
            return Result(str(e), 1)

        finally:
            # Always clean up ephemeral sessions
            if ephemeral and session_thread:
                session_thread.stop_thread()
