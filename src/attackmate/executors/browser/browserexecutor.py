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
        self.log_command(command)

        try:
            # Decide whether we’re using or creating a named session, or ephemeral
            if command.session:
                # We expect an existing session by this name
                if not self.session_store.has_session(command.session):
                    return Result(f"Session '{command.session}' not found!", 1)
                session_thread = self.session_store.get_session(command.session)
            elif command.creates_session:
                # We create a new session
                if self.session_store.has_session(command.creates_session):
                    return Result(f"Session '{command.creates_session}' already exists!", 1)
                session_thread = SessionThread(session_name=command.creates_session)
                self.session_store.set_session(command.creates_session, session_thread)
            else:
                # No session info => ephemeral
                session_thread = SessionThread()

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

            # If this is ephemeral (no session name set or created), close it immediately
            if not command.session and not command.creates_session:
                session_thread.stop_thread()

            return Result('Browser command executed successfully.', 0)

        except Exception as e:
            return Result(str(e), 1)
