"""
sessionexecutor.py
============================================
Close or inspect a session from within a playbook.
"""

from typing import Optional

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.executors.executor_factory import executor_factory
from attackmate.processmanager import ProcessManager
from attackmate.result import Result
from attackmate.schemas.session import SessionCommand
from attackmate.variablestore import VariableStore


@executor_factory.register_executor('session')
class SessionExecutor(BaseExecutor):
    """Acts on the session store of another executor.

    It holds the same executor dictionary AttackMate caches, rather than its
    own store, because a session belongs to whichever executor opened it.
    """

    def __init__(self, pm: ProcessManager, cmdconfig=None, *,
                 varstore: VariableStore, executors: Optional[dict] = None):
        self.executors = executors if executors is not None else {}
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: SessionCommand):
        self.logger.info(f"Session-Command: {command.cmd} '{command.session}' ({command.executor})")

    def get_session_store(self, command: SessionCommand):
        """The store of the executor that owns this kind of session.

        Returns None when that executor has not run yet, which simply means no
        session of that name can exist.
        """
        executor = self.executors.get(command.executor)
        return getattr(executor, 'session_store', None) if executor else None

    async def _exec_cmd(self, command: SessionCommand) -> Result:
        store = self.get_session_store(command)

        if store is None or not self.session_known(store, command.session):
            return Result(f"Session '{command.session}' does not exist", 1)

        if command.cmd == 'status':
            if store.session_is_alive(command.session):
                return Result(f"Session '{command.session}' is alive", 0)
            return Result(f"Session '{command.session}' has exited", 1)

        if store.close_session(command.session):
            return Result(f"Session '{command.session}' closed", 0)
        return Result(f"Session '{command.session}' does not exist", 1)

    @staticmethod
    def session_known(store, session_name: str) -> bool:
        """The shell store holds two kinds of session; the ssh store one."""
        if hasattr(store, 'session_exists'):
            return store.session_exists(session_name)
        return store.has_session(session_name)
