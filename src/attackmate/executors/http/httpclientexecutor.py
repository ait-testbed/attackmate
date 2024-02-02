"""
httpclientexecutor.py
============================================
Execute web-requests
"""

import httpx
from typing import Optional
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.http import HttpClientCommand
from attackmate.execexception import ExecException


class HttpClientExecutor(BaseExecutor):
    def log_command(self, command: HttpClientCommand):
        self.logger.info(f'Performing HTTP[{command.cmd}] to {command.url}')

    def generate_headers(self, command: HttpClientCommand) -> dict[str, str]:
        if not command.headers:
            return {'User-Agent': command.useragent}
        if command.headers:
            if 'User-Agent' not in command.headers.keys():
                command.headers['User-Agent'] = command.useragent
        return command.headers

    def output_headers(self, headers: httpx.Headers) -> str:
        output = ''
        for header_key, header_value in headers.items():
            output += f'{header_key}: {header_value}\n'
        output += '\n'
        return output

    def load_content(self, local_path: Optional[str]) -> bytes | None:
        content = None
        if local_path:
            with open(local_path, 'rb') as f:
                content = f.read()
        return content

    def request_http2(self, command: HttpClientCommand) -> httpx.Response:
        client = httpx.Client(http2=True,
                              headers=self.generate_headers(command),
                              cookies=command.cookies,
                              verify=command.verify)
        response = client.request(command.cmd,
                                  command.url,
                                  content=self.load_content(command.local_path),
                                  follow_redirects=command.follow,
                                  data=command.data)
        return response

    def request(self, command: HttpClientCommand) -> httpx.Response:
        return httpx.request(command.cmd,
                             command.url,
                             content=self.load_content(command.local_path),
                             headers=self.generate_headers(command),
                             cookies=command.cookies,
                             data=command.data,
                             follow_redirects=command.follow,
                             verify=command.verify)

    def _exec_cmd(self, command: HttpClientCommand) -> Result:
        try:
            if command.http2:
                response = self.request_http2(command)
            else:
                response = self.request(command)
        except Exception as e:
            raise ExecException(e)
        if command.output_headers:
            output = self.output_headers(response.headers)
        else:
            output = ''
        output += response.text
        self.logger.debug(f'Status-Code: {response.status_code}')
        self.logger.debug(f'HTTP-Version: {response.http_version}')
        self.varstore.set_variable('LAST_HTTP_STATUS', response.status_code)
        return Result(output, 0)
