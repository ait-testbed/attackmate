import logging
import os
import yaml
from typing import Dict, Any

from attackmate.executors.executor_factory import executor_factory

from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.schemas.remote import AttackMateRemoteCommand
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.processmanager import ProcessManager
from attackmate.variablestore import VariableStore
from attackmate.command import CommandRegistry


@executor_factory.register_executor('remote')
class AttackMateRemoteExecutor(BaseExecutor):
    def __init__(self, pm: ProcessManager, varstore: VariableStore, cmdconfig=None):
        super().__init__(pm, varstore, cmdconfig)
        # self.client is instantiated per command execution
        self.logger = logging.getLogger('playbook')

    def log_command(self, command: AttackMateRemoteCommand):
        self.logger.info(f"Executing REMOTE AttackMate command: Type='{command.type}', RemoteCmd='{command.cmd}' on server {command.server_url}")
