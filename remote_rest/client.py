import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLIENT - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Authentication
CURRENT_TOKEN: Optional[str] = None
# token can then be saved in env var since it does not persit in client memory
TOKEN_ENV_VAR = 'ATTACKMATE_API_TOKEN'


def load_token():
    """Loads token from global or env"""
    global CURRENT_TOKEN
    if CURRENT_TOKEN:
        return CURRENT_TOKEN
    CURRENT_TOKEN = os.getenv(TOKEN_ENV_VAR)
    if CURRENT_TOKEN:
        logger.info('Token loaded')
    return CURRENT_TOKEN


def save_token(token: Optional[str]):
    """Saves token to global var and env"""
    global CURRENT_TOKEN
    CURRENT_TOKEN = token
    if token:
        # This is pretty hacky, client mainly for testing purposes
        logger.info('updating env var')
        logger.info(f"run in your shell: export ATTACKMATE_API_TOKEN={token}")
    else:
        os.environ.pop(TOKEN_ENV_VAR, None)


def get_auth_headers() -> Dict[str, str]:
    token = load_token()
    if token:
        return {'X-Auth-Token': token}
    return {}


def update_token_from_response(data: Dict[str, Any]):
    """Updates the stored token if present in the response data."""
    new_token = data.get('current_token')
    if new_token:
        logger.info('Received renewed token in response')
        save_token(new_token)


#  Helper Functions
def parse_key_value_pairs(items: List[str] | None) -> Dict[str, str]:
    """Helper to parse 'key=value' strings from a list into a dict."""
    result: Dict[str, str] = {}
    if not items:
        return result
    for item in items:
        if '=' in item:
            key, value = item.split('=', 1)
            result[key.strip()] = value.strip()
        else:
            logging.warning(f"Skipping malformed pair: {item}")
    return result


# Login
def login(client: httpx.Client, base_url: str, username: str, password: str):
    """Logs in and saves the token."""
    url = f"{base_url}/login"
    logger.info(f"Attempting login for user '{username}' at {url}...")
    try:
        # standard form encoding for OAuth2PasswordRequestForm -> expected bei Fastapi
        response = client.post(url, data={'username': username, 'password': password})
        response.raise_for_status()
        data = response.json()
        token = data.get('access_token')
        if token:
            save_token(token)  # workaround, export to env var in shell
            print(f"Login successful. Token received: {token[:5]}...")
        else:
            logger.error(' No access token received in response.')
            sys.exit(1)
    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error during login: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        logger.error(f"Login failed: {e.response.status_code}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        sys.exit(1)


def get_instance_state_from_server(client: httpx.Client, base_url: str, instance_id: str):
    """Requests the state of a specific instance."""
    url = f"{base_url}/instances/{instance_id}/state"
    logger.info(f"Requesting state for instance {instance_id} at {url}...")
    try:
        response = client.get(url, headers=get_auth_headers())
        response.raise_for_status()
        data = response.json()
        update_token_from_response(data)
        print(f"\n State for Instance {instance_id} ")
        print(yaml.dump(data.get('variables', {}), indent=2))
    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error getting state: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error getting state: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error getting state: {e}", exc_info=True)


def run_playbook_yaml(
    client: httpx.Client, base_url: str, playbook_file: str, debug: bool = False
):
    """Sends playbook YAML content to the server."""
    url = f"{base_url}/playbooks/execute/yaml"
    logger.info(f"Attempting to execute playbook from local file: {playbook_file}")
    try:
        with open(playbook_file, 'r') as f:
            playbook_yaml_content = f.read()
    except Exception as e:
        logger.error(f"Error reading file '{playbook_file}': {e}")
        sys.exit(1)
    try:
        params = {'debug': True} if debug else {}
        response = client.post(url, content=playbook_yaml_content, headers={**get_auth_headers(),
                               'Content-Type': 'application/yaml'}, params=params)
        response.raise_for_status()
        data = response.json()
        update_token_from_response(data)
        print('\n Playbook YAML Execution Result ')
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print(f"ID: {data.get('instance_id')}")
        if data.get('final_state'):
            print('\n Final Variable Store State ')
            print(yaml.dump(data['final_state'].get('variables', {}), indent=2))
        if not data.get('success'):
            sys.exit(1)
    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error executing playbook YAML: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error (YAML): {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error (YAML): {e}", exc_info=True)
        sys.exit(1)


def run_playbook_file(
    client: httpx.Client,
    base_url: str,
    playbook_file_path_on_server: str,
    debug: bool = False
):
    """Requests server to execute a playbook from local path."""
    url = f"{base_url}/playbooks/execute/file"
    logger.info(f"Requesting server execute playbook file: {playbook_file_path_on_server}")
    payload = {'file_path': playbook_file_path_on_server}
    try:
        params = {'debug': True} if debug else {}
        response = client.post(url, json=payload, params=params, headers=get_auth_headers())
        response.raise_for_status()
        data = response.json()
        update_token_from_response(data)
        print('\n Playbook File Execution Result ')
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print(f"ID: {data.get('instance_id')}")
        if data.get('final_state'):
            print('\n Final Variable Store State ')
            print(yaml.dump(data['final_state'].get('variables', {}), indent=2))
        if not data.get('success'):
            sys.exit(1)
    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error executing playbook file: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error (File): {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error (File): {e}", exc_info=True)
        sys.exit(1)


def run_command(client: httpx.Client, base_url: str, args):
    """Sends a single command to the server for execution against an instance."""
    # TODO this need more special handling for sliver commands?
    type = args.type

    url = f"{base_url}/command/{type.replace('_', '-')}"
    logger.info(f"Attempting command '{type}' on instance 'default_context' at {url}")

    # Construct the request body dictionary (matching Pydantic model)
    # Exclude argparse internals
    body_dict: Dict[str, Any] = {}
    excluded_args = {'mode', 'func', 'server_url', 'instance_id'}
    for arg_name, arg_value in vars(args).items():
        if arg_name not in excluded_args and arg_value is not None:
            pydantic_field_name = arg_name
            # Type conversions for body (Pydantic/FastAPI handles validation, but ensure basic types)
            if arg_name in [
                'option', 'payload_option', 'metadata', 'prompts',
                'output_map', 'header', 'cookie', 'data'
            ]:
                if isinstance(arg_value, list):
                    body_dict[pydantic_field_name] = parse_key_value_pairs(arg_value)
            else:
                body_dict[pydantic_field_name] = arg_value

    try:
        logger.debug(f"Sending POST to {url}")
        logger.debug(f"Request Body: {json.dumps(body_dict, indent=2)}")
        response = client.post(url, json=body_dict, headers=get_auth_headers())
        response.raise_for_status()
        data = response.json()
        update_token_from_response(data)
        logger.info(f"Received response from /{type} endpoint.")
        logger.debug(f"Response data: {data}")

        result = data.get('result', {})
        state = data.get('state', {}).get('variables', {})

        print('\n--- Command Result ---')
        print(f"Success: {result.get('success')}")
        print(f"Return Code: {result.get('returncode')}")
        print(f"Stdout:\n{result.get('stdout')}")
        if result.get('error_message'):
            print(f"Error Message: {result.get('error_message')}")

        print('\n--- Updated Variable Store State --- ')
        print(yaml.dump(state, indent=2, default_flow_style=False))

        is_background = hasattr(args, 'background') and args.background is True
        if not result.get('success') or (result.get('returncode') != 0 and not is_background):
            sys.exit(1)

    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error executing command: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error ({url}): {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error executing command: {e}", exc_info=True)
        sys.exit(1)


#  Main Execution Logic
def main():
    parser = argparse.ArgumentParser(description='AttackMate REST API Client')
    parser.add_argument('--base-url', default='https://localhost:8443',
                        help='Base URL of the AttackMate API server')
    parser.add_argument(
        '--cacert',
        help='Path to the server\'s self-signed certificate file (cert.pem) for verification.'
    )
    subparsers = parser.add_subparsers(dest='mode', required=True, help='Operation mode')

    # Login Mode
    parser_login = subparsers.add_parser('login', help='Authenticate and get a token')
    parser_login.add_argument('username', help='API username')
    parser_login.add_argument('password', help='API password')

    #  Playbook Modes
    parser_pb_yaml = subparsers.add_parser(
        'playbook-yaml', help='Execute a playbook from a local YAML file content')
    parser_pb_yaml.add_argument('playbook_file', help='Path to the local playbook YAML file')
    parser_pb_yaml.add_argument('--debug', action=argparse.BooleanOptionalAction,
                                help='Enable server debug logging for this instance')

    parser_pb_file = subparsers.add_parser(
        'playbook-file', help='Request server execute a playbook from its filesystem')
    parser_pb_file.add_argument('server_playbook_path',
                                help='Path to the playbook file relative to the server\'s allowed directory')
    parser_pb_file.add_argument('--debug', action=argparse.BooleanOptionalAction,
                                help='Enable server debug logging for this instance')

    parser_inst_state = subparsers.add_parser('instance-state', help='Get the state of an instance')
    parser_inst_state.add_argument('instance_id', help='ID of the instance')

    #  Command Mode
    parser_command = subparsers.add_parser('command', help='Execute a single command on a specific instance')
    command_subparsers = parser_command.add_subparsers(
        dest='type', required=True, help='Specific command type')

    # Define Common Arguments Parser (used as parent for command types)
    common_args_parser = argparse.ArgumentParser(add_help=False)
    common_args_parser.add_argument('--only-if', help='Conditional execution string')
    common_args_parser.add_argument('--error-if', help='Regex pattern for error on match')
    common_args_parser.add_argument('--error-if-not', help='Regex pattern for error if no match')
    common_args_parser.add_argument('--loop-if', help='Regex pattern to loop on match')
    common_args_parser.add_argument('--loop-if-not', help='Regex pattern to loop if no match')
    common_args_parser.add_argument('--loop-count', type=int, help='Maximum loop iterations')
    common_args_parser.add_argument(
        '--exit-on-error',
        action=argparse.BooleanOptionalAction,
        help='Exit if command return code is non-zero'
    )
    common_args_parser.add_argument('--save', help='File path to save command stdout')
    common_args_parser.add_argument(
        '--background', action=argparse.BooleanOptionalAction, help='Run command in the background')
    common_args_parser.add_argument(
        '--kill-on-exit', action=argparse.BooleanOptionalAction, help='Kill process on server exit')
    common_args_parser.add_argument('--metadata', action='append',
                                    help='Metadata key=value pair (repeatable)')

    #  Add Command Subparsers
    # Shell
    parser_shell = command_subparsers.add_parser(
        'shell', help='Execute shell command', parents=[common_args_parser])
    parser_shell.add_argument('cmd', help='The command to execute')
    parser_shell.add_argument('--interactive', action=argparse.BooleanOptionalAction)
    parser_shell.add_argument('--creates-session', help='Name of shell session to create')
    parser_shell.add_argument('--session', help='Name of existing shell session to use')
    parser_shell.add_argument('--command-timeout', type=int)
    parser_shell.add_argument('--read', action=argparse.BooleanOptionalAction, default=True)
    parser_shell.add_argument('--command-shell', help='Shell path')
    parser_shell.add_argument('--bin', action=argparse.BooleanOptionalAction)

    # Sleep
    parser_sleep = command_subparsers.add_parser(
        'sleep', help='Pause execution', parents=[common_args_parser])
    parser_sleep.add_argument('--seconds', type=int)
    parser_sleep.add_argument('--min-sec', type=int)
    parser_sleep.add_argument('--random', action=argparse.BooleanOptionalAction)

    # Debug
    parser_debug = command_subparsers.add_parser(
        'debug', help='Debug output or pause', parents=[common_args_parser])
    parser_debug.add_argument('--varstore', action=argparse.BooleanOptionalAction)
    parser_debug.add_argument('--exit', action=argparse.BooleanOptionalAction)
    parser_debug.add_argument('--wait-for-key', action=argparse.BooleanOptionalAction)

    # SetVar
    parser_setvar = command_subparsers.add_parser(
        'setvar', help='Set a variable', parents=[common_args_parser])
    parser_setvar.add_argument('variable', help='Name of the variable to set')
    parser_setvar.add_argument('cmd', help='Value to assign to the variable')
    parser_setvar.add_argument('--encoder', help='Encoder to use')

    # Mktemp (Tempfile)
    parser_mktemp = command_subparsers.add_parser(
        'mktemp', help='Create temporary file/directory', parents=[common_args_parser])
    parser_mktemp.add_argument('variable', help='Variable name to store the path')
    parser_mktemp.add_argument('--cmd', choices=['file', 'dir'],
                               default='file', help='create a file or directory')

    #  ADD SUBPARSERS FOR ALL OTHER COMMAND TYPES HERE

    args = parser.parse_args()
    if args.cacert:
        cert_path = os.path.abspath(args.cacert)  # Ensure absolute path
        if os.path.exists(cert_path):
            logger.info(f"Configured httpx to verify using CA cert: {cert_path}")
        else:
            logger.error(f"CA certificate file not found at specified path: {cert_path}")
            sys.exit(1)

    #  Create HTTP Client
    with httpx.Client(base_url=args.base_url, timeout=60.0, verify=cert_path) as client:
        try:
            #  Execute based on mode
            if args.mode == 'login':
                login(client, args.base_url, args.username, args.password)
            if args.mode == 'playbook-yaml':
                run_playbook_yaml(client, args.base_url, args.playbook_file, args.debug)
            elif args.mode == 'playbook-file':
                run_playbook_file(client, args.base_url, args.server_playbook_path, args.debug)
            elif args.mode == 'instance-state':
                get_instance_state_from_server(client, args.base_url, args.instance_id)
            elif args.mode == 'command':
                if hasattr(args, 'type') and args.type:
                    run_command(client, args.base_url, args)
                else:
                    logger.error('Internal error: Command mode selected but no command type specified.')
                    parser.print_help()
                    sys.exit(1)
        except httpx.ConnectError as e:
            logger.error(
                f"Connection Error: Could not connect to {args.base_url}. "
                f"Is the server running with HTTPS? Did you provide cert? Details: {e}"
            )
            sys.exit(1)
        except Exception as main_err:
            logger.error(f"Client execution failed: {main_err}", exc_info=True)
            sys.exit(1)

    logger.info('Client finished.')


if __name__ == '__main__':
    main()
