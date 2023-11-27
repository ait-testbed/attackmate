"""
webservexecutor.py
============================================
Serves files via HTTP
"""

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.schemas.http import WebServCommand
from attackmate.executors.features.cmdvars import CmdVars
from http.server import HTTPServer, BaseHTTPRequestHandler
import magic


class WebRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, local_path=None, **kwargs):
        self.local_path = local_path
        super().__init__(*args, **kwargs)

    def get_contenttype_from_file(self):
        mime = magic.Magic(mime=True)
        return mime.from_file(self.local_path)

    def load_file(self):
        data = None
        with open(self.local_path, 'rb') as f:
            data = f.read()
        return data

    def do_GET(self):
        msg = self.load_file()
        self.send_response(200)
        self.protocol_version = 'HTTP/1.1'
        self.send_header('Content-length', len(msg))
        self.send_header('Content-Type', self.get_contenttype_from_file())
        self.end_headers()
        self.wfile.write(msg)


class WebServe(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, *, local_path: str):
        self.local_path = local_path
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

    def finish_request(self, request, client_address):
        try:
            self.RequestHandlerClass(request, client_address, self,
                                     local_path=self.local_path)
        except ConnectionResetError:
            pass


class WebServExecutor(BaseExecutor):

    def log_command(self, command: WebServCommand):
        self.logger.info(f'Serving {command.local_path} via HTTP on Port {command.port}')

    def _exec_cmd(self, command: WebServCommand) -> Result:
        address = (command.address, CmdVars.variable_to_int('Port', command.port))
        try:
            server = WebServe(address, WebRequestHandler, local_path=command.local_path)
            server.handle_request()
        except Exception as e:
            raise ExecException(e)

        return Result(f'Delivered {command.local_path}', 0)
