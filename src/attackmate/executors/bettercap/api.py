from urllib.parse import urljoin, urlencode
from typing import Mapping, Tuple, Optional

"""
Api-docs: https://www.bettercap.org/modules/core/apirest/
"""


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
        return self._request_with_parameter('/api/events', 'GET')

    def delete_api_events(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/events', 'DELETE')

    def get_session_modules(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/modules', 'GET')

    def get_session_env(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/env', 'GET')

    def get_session_gateway(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/gateway', 'GET')

    def get_session_hid(self, mac: Optional[str] = None) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/hid', 'GET', mac)

    def get_session_ble(self, mac: Optional[str] = None) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/ble', 'GET', mac)

    def get_session_interface(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/interface', 'GET')

    def get_session_lan(self, mac: Optional[str] = None) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/lan', 'GET', mac)

    def get_session_options(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/options', 'GET')

    def get_session_packets(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/packets', 'GET')

    def get_session_started_at(self) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/started-at', 'GET')

    def get_session_wifi(self, mac: Optional[str] = None) -> Tuple[int, Mapping[str, str], bytes]:
        return self._request_with_parameter('/api/session/wifi', 'GET', mac)

    def _request_with_parameter(self, url: str,
                                method: str,
                                param: Optional[str] = None) -> Tuple[int, Mapping[str, str], bytes]:
        if not self.server:
            self.server = ''
        api_url: str = urljoin(self.server, url)
        if param:
            api_url + '/' + param
        return self._request(method, api_url, headers=self.headers)

    def _request(self,
                 method: str,
                 url: str,
                 headers: Mapping[str, str],
                 json_data: dict = {}
                 ) -> Tuple[int, Mapping[str, str], bytes]:
        raise Exception('Not implemented yet')
