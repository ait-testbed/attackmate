import time
import logging
from typing import Dict, Optional
from multiprocessing import JoinableQueue
from attackmate.variablestore import VariableStore
from attackmate.execexception import ExecException


class MsfSessionStore:
    def __init__(self, varstore: VariableStore) -> None:
        self.sessions: Dict[str, Dict[str, str]] = {}
        self.logger = logging.getLogger('playbook')
        self.varstore = varstore
        self.queue: Optional[JoinableQueue] = None
        self.get_session_wait_time = 5

    def _conn_sessions(self, conn_name: str) -> Dict[str, str]:
        if conn_name not in self.sessions:
            self.sessions[conn_name] = {}
        return self.sessions[conn_name]

    def add_session(self, conn_name: str, name: str, uuid: str) -> None:
        self.logger.debug(f'Set MSF-Session [{conn_name}]: {name} = {uuid}')
        self._conn_sessions(conn_name)[name] = uuid

    def get_session_by_name(self, conn_name: str, name: str, msfsessions, block: bool = True) -> str:
        conn_sessions = self._conn_sessions(conn_name)
        while True:
            if self.queue:
                while not self.queue.empty():
                    item = self.queue.get()
                    # item: (conn_name, session_name, uuid, session_id)
                    self.logger.debug(f'Session from Queue: [{item[0]}] {item[1]} = {item[2]}')
                    self.add_session(item[0], item[1], item[2])
                    self.logger.debug(f'Set LAST_MSF_SESSION to {item[3]}')
                    self.varstore.set_variable('LAST_MSF_SESSION', item[3])
                    self.varstore.set_variable(f'LAST_MSF_SESSION_{item[0]}', item[3])
                    self.queue.task_done()
                    time.sleep(self.get_session_wait_time)
            for k, v in msfsessions.list.items():
                if name in conn_sessions:
                    if v['exploit_uuid'] == conn_sessions[name]:
                        return k
                    else:
                        self.logger.debug(
                            f'uuid {conn_sessions[name]} does not match with any entry in sessions')
                else:
                    self.logger.debug(f'{name} not found in msfsessions for connection {conn_name}')

            if not block:
                raise ExecException(f'Session ({name}) not found')
            else:
                time.sleep(3)

    def add_or_queue_session(self, conn_name: str, name: str, uuid: str,
                             queue: Optional[JoinableQueue] = None,
                             session_id: Optional[int] = None):
        seconds = 30
        if queue:
            queue.put((conn_name, name, uuid, session_id))
        else:
            self.add_session(conn_name, name, uuid)
            self.logger.debug(f'Set LAST_MSF_SESSION: {session_id}')
            self.varstore.set_variable('LAST_MSF_SESSION', str(session_id))
            self.varstore.set_variable(f'LAST_MSF_SESSION_{conn_name}', str(session_id))
            self.logger.debug(f'Waiting {seconds} seconds for session to get ready')
            time.sleep(seconds)

    def wait_for_session(self, conn_name: str, name: str, uuid: str, msfsessions,
                         queue: Optional[JoinableQueue] = None):
        self.logger.debug(f'Sessions: {msfsessions.list}')
        while True:
            if len(list(msfsessions.list.keys())) > 0:
                for session_id, v in msfsessions.list.items():
                    if v['exploit_uuid'] == uuid:
                        self.add_or_queue_session(conn_name, name, uuid, queue, session_id)
                        return

    def wait_for_increased_session(self, conn_name: str, name: str, uuid: str, msfsessions,
                                   queue: Optional[JoinableQueue] = None):
        stored_list_len = len(list(msfsessions.list.keys()))
        sessions = list(msfsessions.list.keys())
        while True:
            if len(list(msfsessions.list.keys())) > stored_list_len:
                for session_id, v in msfsessions.list.items():
                    if session_id not in sessions:
                        self.add_or_queue_session(conn_name, name, v['exploit_uuid'], queue, session_id)
                        self.logger.debug(f'Sessions: {msfsessions.list}')
                        return
