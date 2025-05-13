import httpx
import logging
import os
import json
from typing import Dict, Any, Optional

_active_sessions: Dict[str, Dict[str, str]] = {}
DEFAULT_TIMEOUT = 60.0  # what should the timeout be for requests? what about background?
# make timeout configurable?

logger = logging.getLogger('playbook')


class RemoteAttackMateClient:
    """
    Client to interact with a remote AttackMate REST API.
    Handles authentication and token management internally per server URL.
    """
    def __init__(
        self,
        server_url: str,
        cacert: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout_config = httpx.Timeout(10.0, connect=5.0, read=timeout)

        if cacert:
            if os.path.exists(cacert):
                self.verify_ssl = cacert
                logger.info(f"Client will verify {self.server_url} SSL using CA: {cacert}")
            else:
                logger.error(f"CA certificate file not found: {cacert}.")
        logger.debug(f"RemoteClient initialized for {self.server_url}")

    def _get_session_token(self) -> Optional[str]:
        """Retrieves a valid token for the server_url from memory, logs in if necessary."""
        # There is a token for that server and user in memory, use that
        session_data = _active_sessions.get(self.server_url)
        if session_data and session_data.get('user') == self.username:
            logger.debug(f"Using existing token for {self.server_url} by user {session_data['user']}")
            return session_data['token']
        # if not try login with credentials
        else:
            if self.username and self.password:
                return self._login(self.username, self.password)
        return None

    def _login(self, username: str, password: str) -> Optional[str]:
        """Internal login method, stores token."""
        login_url = f"{self.server_url}/login"
        logger.info(f"Attempting login to {login_url} for user '{username}'...")
        try:
            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout_config) as client:
                response = client.post(login_url, data={'username': username, 'password': password})
                # does this need to be form data?

            response.raise_for_status()
            data = response.json()
            token = data.get('access_token')

            if token:
                # with a session_lock?
                _active_sessions[self.server_url] = {
                    'token': token,
                    'user': username
                }
                logger.info(f"Login successful for '{username}' at {self.server_url}. Token stored.")
                return token
            else:
                logger.error(f"Login to {self.server_url} succeeded but no token received.")
                return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Login failed for '{username}' at {self.server_url}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Login request to {self.server_url} failed: {e}", exc_info=True)
            return None

    # Common Method to make request
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        content_data: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Makes an authenticated request, handles token renewal implicitly by server."""
        token = self._get_session_token()
        if not token:
            # Attempt login if credentials are set on the client instance
            if self.username and self.password:
                logger.info(
                    f"No active token for {self.server_url}, try login with provided credentials."
                )
                token = self._login(self.username, self.password)
            if not token:
                logger.error(f"Auth required for {self.server_url} but no token available and login failed")
                return None  # Or raise an AuthException?

        headers = {'X-Auth-Token': token}
        if content_data:
            headers['Content-Type'] = 'application/yaml'

        url = f"{self.server_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making {method.upper()} request to {url}")
        try:
            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout_config) as client:
                if method.upper() == 'POST':
                    if content_data:
                        # sending yaml playbook content
                        response = client.post(url, content=content_data, headers=headers, params=params)
                    else:
                        # sending command or file path
                        response = client.post(url, json=json_data, headers=headers, params=params)
                elif method.upper() == 'GET':
                    response = client.get(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            response_data = response.json()

            # Server should renew token on any successful authenticated API call.
            # Client just uses the token. Server sends back a new token if renewed,
            # The current_token field in the response from server use to update client's token.
            new_token_from_response = response_data.get('current_token')
            if new_token_from_response and new_token_from_response != token:
                logger.info(f"Server returned a renewed token for {self.server_url}. Updating client.")
                _active_sessions[self.server_url]['token'] = new_token_from_response
            return response_data

        except httpx.HTTPStatusError as e:
            logger.error(f"API Error ({method} {url}): {e.response.status_code}")
            if e.response.status_code == 401:  # Unauthorized
                logger.warning(f"Token likely expired or invalid for {self.server_url}. Clearing token")
                # with _session_lock:
                _active_sessions.pop(self.server_url, None)  # Clear session on 401
            return None  # Or raise custom Error?
        except httpx.RequestError as e:
            logger.error(f"Request Error ({method} {url}): {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"JSON Decode Error ({method} {url}). Response: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during API request ({method} {url}): {e}", exc_info=True)
            return None

    # API Methods all use the _make_request method
    def execute_remote_playbook_yaml(
        self, playbook_yaml_content: str, debug: bool = False
    ) -> Optional[Dict[str, Any]]:
        return self._make_request(
            method='POST',
            endpoint='playbooks/execute/yaml',
            content_data=playbook_yaml_content,
            params={'debug': True} if debug else None
        )

    def execute_remote_playbook_file(
        self, server_playbook_path: str, debug: bool = False
    ) -> Optional[Dict[str, Any]]:
        return self._make_request(
            method='POST',
            endpoint='playbooks/execute/file',
            json_data={'file_path': server_playbook_path},
            params={'debug': True} if debug else None
        )

    def execute_remote_command(
        self,
        command_pydantic_model,
        debug: bool = False
    ) -> Optional[Dict[str, Any]]:
        # get the correct enpoint
        command_type_for_path = command_pydantic_model.type.replace('_', '-')  # API path has hyphens
        endpoint = f"command/{command_type_for_path}"

        # Convert Pydantic model to dict for JSON body
        # handle None values for optional fields (exclude_none=True)
        command_body_dict = command_pydantic_model.model_dump(exclude_none=True)

        return self._make_request(
            method='POST',
            endpoint=endpoint,
            json_data=command_body_dict,
            params={'debug': True} if debug else None
        )
