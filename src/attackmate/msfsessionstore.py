import time
import logging
from typing import Dict
from attackmate.variablestore import VariableStore
from .execexception import ExecException


class MsfSessionStore:
    def __init__(self, varstore: VariableStore) -> None:
        self.sessions: Dict[str, str] = {}
        self.logger = logging.getLogger('playbook')
        self.varstore = varstore

    def add_session(self, name: str, uuid: str) -> None:
        self.sessions[name] = uuid

    def get_session_by_name(self, name: str, msfsessions) -> str:
        for k, v in msfsessions.list.items():
            if v['exploit_uuid'] == self.sessions[name]:
                return k
        raise ExecException(f"Session ({name}) not found")

    def wait_for_session(self, name: str, uuid: str, msfsessions):
        seconds = 30

        self.logger.debug(f"Sessions: {msfsessions.list}")
        while True:
            if len(list(msfsessions.list.keys())) > 0:
                for k, v in msfsessions.list.items():
                    if v['exploit_uuid'] == uuid:
                        self.add_session(name, uuid)
                        self.varstore.set_variable("LAST_MSF_SESSION", k)
                        self.logger.debug(f"Waiting {seconds} seconds for session to get ready")
                        time.sleep(seconds)
                        return
