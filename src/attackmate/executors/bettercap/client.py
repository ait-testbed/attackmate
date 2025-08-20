import httpx
import ssl
from typing import Any, Mapping, Tuple
from .api import Api

class Client(Api):
    def __init__(self, 
                 *args: Any,
                 **kwargs: Any
                 ) -> None:
        self.headers: dict[str,str] = {}
        self.server = args[0]
        self._client = httpx.Client(**kwargs)

    def user_agent(self, user_agent: str) -> None:
        self.headers["User-Agent"] = user_agent

    def basic_auth(self, username:str, password: str) -> None:
        auth: BasicAuth = httpx.BasicAuth(username=username, password=password)
        self._client.auth = auth

    def ca_file(self, cafile: str) -> None:
        ctx: SSLContext = ssl.create_default_context(cafile=cafile)
        self._client.verify = ctx

    def _request(self,
                 method: str,
                 url: str,
                 headers: Mapping[str, str],
                 json_data: dict = {}
                 ) -> Tuple[int, Mapping[str, str], bytes]:
        response = self._client.request(
                method, url, headers=dict(headers), json=json_data
        )
        return response.status_code, response.headers, response.content


