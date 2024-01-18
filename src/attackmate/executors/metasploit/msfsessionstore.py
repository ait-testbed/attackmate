import time
import logging
from typing import Dict, Optional
from multiprocessing import JoinableQueue
from attackmate.variablestore import VariableStore
from attackmate.execexception import ExecException


class MsfSessionStore:
    def __init__(self, varstore: VariableStore) -> None:
        self.sessions: Dict[str, str] = {}
        self.logger = logging.getLogger('playbook')
        self.varstore = varstore
        self.queue: Optional[JoinableQueue] = None
        self.get_session_wait_time = 5

    def add_session(self, name: str, uuid: str) -> None:
        self.logger.debug(f'Set MSF-Session: {name} = {uuid}')
        self.sessions[name] = uuid

    def get_session_by_name(self, name: str, msfsessions, block: bool = True) -> str:
        while True:
            if self.queue:
                while not self.queue.empty():
                    item = self.queue.get()
                    self.logger.debug(f'Session from Queue: {item[0]} = {item[1]}')
                    self.add_session(item[0], item[1])
                    self.logger.debug(f'Set LAST_MSF_SESSION to {item[2]}')
                    self.varstore.set_variable('LAST_MSF_SESSION', item[2])
                    self.queue.task_done()
                    time.sleep(self.get_session_wait_time)
            for k, v in msfsessions.list.items():
                if name in self.sessions:
                    if v['exploit_uuid'] == self.sessions[name]:
                        return k
                    else:
                        self.logger.debug(f"uuid {self.sessions[name]} does not match with any entry in sessions")
                else:
                    self.logger.debug(f"{name} not found in msfsessions")

            if not block:
                raise ExecException(f'Session ({name}) not found')
            else:
                time.sleep(3)

    def add_or_queue_session(self, name: str, uuid: str, queue: Optional[JoinableQueue] = None,
                             session_id: Optional[int] = None):
        seconds = 30
        if queue:
            queue.put((name, uuid, session_id))
        else:
            self.add_session(name, uuid)
            self.logger.debug(f'Set LAST_MSF_SESSION: {session_id}')
            self.varstore.set_variable('LAST_MSF_SESSION', str(session_id))
            self.logger.debug(f'Waiting {seconds} seconds for session to get ready')
            time.sleep(seconds)

    def wait_for_session(self, name: str, uuid: str, msfsessions, queue: Optional[JoinableQueue] = None):
        self.logger.debug(f'Sessions: {msfsessions.list}')
        while True:
            if len(list(msfsessions.list.keys())) > 0:
                for session_id, v in msfsessions.list.items():
                    if v['exploit_uuid'] == uuid:
                        self.add_or_queue_session(name, uuid, queue, session_id)
                        return

    def wait_for_increased_session(self, name: str, uuid: str, msfsessions,
                                   queue: Optional[JoinableQueue] = None):
        stored_list_len = len(list(msfsessions.list.keys()))
        sessions = list(msfsessions.list.keys())
        while True:
            if len(list(msfsessions.list.keys())) > stored_list_len:
                for session_id, v in msfsessions.list.items():
                    if session_id not in sessions:
                        self.add_or_queue_session(name, v['exploit_uuid'], queue, session_id)
                        self.logger.debug(f'Sessions: {msfsessions.list}')
                        return
