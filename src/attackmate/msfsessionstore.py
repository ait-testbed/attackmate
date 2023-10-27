import time
import logging
from typing import Dict
from multiprocessing import Queue
from attackmate.variablestore import VariableStore
from .execexception import ExecException


class MsfSessionStore:
    def __init__(self, varstore: VariableStore) -> None:
        self.sessions: Dict[str, str] = {}
        self.logger = logging.getLogger('playbook')
        self.varstore = varstore
        self.queue = None

    def add_session(self, name: str, uuid: str) -> None:
        self.sessions[name] = uuid

    def get_session_by_name(self, name: str, msfsessions, block: bool = True) -> str:
        while True:
            if self.queue:
                while not self.queue.empty():
                    item = self.queue.get()
                    self.logger.debug(f"Read {item[0]} {item[1]} from queue")
                    self.add_session(item[0], item[1])
                    self.queue.task_done()
            for k, v in msfsessions.list.items():
                if name in self.sessions:
                    if v['exploit_uuid'] == self.sessions[name]:
                        return k
            if not block:
                raise ExecException(f"Session ({name}) not found")
            else:
                time.sleep(3)

    def wait_for_session(self, name: str, uuid: str, msfsessions, queue: Queue = None):
        seconds = 30

        self.logger.debug(f"Sessions: {msfsessions.list}")
        while True:
            if len(list(msfsessions.list.keys())) > 0:
                for k, v in msfsessions.list.items():
                    if v['exploit_uuid'] == uuid:
                        if queue:
                            queue.put((name, uuid))
                        else:
                            self.add_session(name, uuid)
                            self.varstore.set_variable("LAST_MSF_SESSION", k)
                            self.logger.debug(f"Waiting {seconds} seconds for session to get ready")
                            time.sleep(seconds)
                        return
