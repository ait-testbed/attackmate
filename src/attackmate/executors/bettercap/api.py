from urllib.parse import urljoin, urlencode
from typing import Mapping, Tuple, Optional


class Api:
    def __init__(self) -> None:
        self.server: Optional[str] = None
        self.headers: dict[str, str] = {}

    def get_file(self, filename) -> Tuple[int, Mapping[str, str], bytes]:
        params = {'name': filename}
        if not self.server:
            self.server = ''
        url: str = urljoin(self.server, '/api/file') + '?' + urlencode(params)
        return self._request('GET', url, headers=self.headers)

    def post_api_session(self, body) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('POST',
                             urljoin(self.server, '/api/session'),
                             headers=self.headers, json_data=body)

    def get_events(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET',  urljoin(self.server, '/api/events'), headers=self.headers)

    def delete_api_events(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('DELETE',  urljoin(self.server, '/api/events'), headers=self.headers)

    def get_session_modules(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/modules'), headers=self.headers)

    def get_session_env(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/env'), headers=self.headers)

    def get_session_gateway(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/gateway'), headers=self.headers)

    def get_session_hid(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/hid'), headers=self.headers)

    def get_session_ble(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/ble'), headers=self.headers)

    def get_session_interface(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/interface'), headers=self.headers)

    def get_session_lan(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/lan'), headers=self.headers)

    def get_session_options(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/options'), headers=self.headers)

    def get_session_packets(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/packets'), headers=self.headers)

    def get_session_started_at(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/started-at'), headers=self.headers)

    def get_session_wifi(self) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        return self._request('GET', urljoin(self.server, '/api/session/wifi'), headers=self.headers)

    def _request(self,
                 method: str,
                 url: str,
                 headers: Mapping[str, str],
                 json_data: dict = {}
                 ) -> Tuple[int, Mapping[str, str], bytes]:
        raise Exception('Not implemented yet')
