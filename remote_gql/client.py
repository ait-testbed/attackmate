import httpx
import argparse
import yaml
import logging
import sys
import json
from typing import Dict, Any, List
import stringcase


# HELPER
def parse_key_value_pairs(items: List[str] | None) -> Dict[str, str]:
    """Helper to parse 'key=value' strings from a list into a dict."""
    result: Dict[str, str] = {}
    if not items:
        return result
    for item in items:
        if '=' in item:
            key, value = item.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def convert_keys_to_camel_case(data: Any) -> Any:
    """Recursively converts dictionary keys from snake_case to camelCase with stringcase library."""
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_key = stringcase.camelcase(key)
            new_dict[new_key] = convert_keys_to_camel_case(value)
        return new_dict
    elif isinstance(data, list):
        return [convert_keys_to_camel_case(item) for item in data]
    else:
        return data


logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLIENT - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_remote_playbook(client: httpx.Client, server_url: str, playbook_file: str):
    """Sends playbook file path to the server for execution."""
    logger.info(f"Attempting to execute remote playbook: {playbook_file}")

    # GraphQL Mutation String
    mutation = """
        mutation ExecuteRemotePlaybook($filepath: String!) {
            executeRemotePlaybook(playbookFilePath: $filepath) {
                success
                message
                finalState {
                    variables
                }
            }
        }
    """
    variables = {'filepath': playbook_file}

    try:
        logger.debug(f"Sending mutation: {mutation}")
        logger.debug(f"Variables: {variables}")
        response = client.post(server_url, json={'query': mutation, 'variables': variables})
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        logger.info('Received response from executeRemotePlaybook.')
        logger.debug(f"Response data: {data}")

        if 'errors' in data:
            logger.error(f"GraphQL Errors: {data['errors']}")
            sys.exit(1)

        result = data.get('data', {}).get('executeRemotePlaybook', {})
        print('\n--- Remote Playbook Execution Result ---')
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print('\n--- Final Variable Store State ---')
        final_state = result.get('finalState', {}).get('variables', {})
        print(yaml.dump(final_state, indent=2, default_flow_style=False))

        if not result.get('success'):
            sys.exit(1)

    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error executing remote playbook: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error executing remote playbook: {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


def run_playbook(client: httpx.Client, server_url: str, playbook_file: str):
    """Sends playbook YAML file to the server for execution."""
    logger.info(f"Attempting to execute playbook: {playbook_file}")

    try:
        with open(playbook_file, 'r') as f:
            playbook_yaml_content = f.read()
    except FileNotFoundError:
        logger.error(f"Error: Playbook file not found at '{playbook_file}'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading playbook file '{playbook_file}': {e}")
        sys.exit(1)

    # GraphQL Mutation String
    mutation = """
        mutation ExecutePlaybook($yaml: String!) {
            executePlaybook(playbookYaml: $yaml) {
                success
                message
                finalState {
                    variables
                }
            }
        }
    """
    variables = {'yaml': playbook_yaml_content}

    try:
        logger.debug(f"Sending mutation: {mutation}")
        logger.debug(f"Variables: {variables}")
        response = client.post(server_url, json={'query': mutation, 'variables': variables})
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        logger.info('Received response from executePlaybook.')
        logger.debug(f"Response data: {data}")

        if 'errors' in data:
            logger.error(f"GraphQL Errors: {data['errors']}")
            sys.exit(1)

        result = data.get('data', {}).get('executePlaybook', {})
        print('\n--- Playbook Execution Result ---')
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print('\n--- Final Variable Store State ---')
        final_state = result.get('finalState', {}).get('variables', {})
        print(yaml.dump(final_state, indent=2, default_flow_style=False))

        if not result.get('success'):
            sys.exit(1)

    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error executing playbook: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error executing playbook: {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


def run_command(client: httpx.Client, server_url: str, args):
    """Sends a single command to the server for execution."""
    logger.info(f"Attempting to execute command: type='{args.command_type}'")

    # onstruct the  input dictionary from args
    command_input: Dict[str, Any] = {'type': args.command_type}

    # Add cmd, sometimesbased on type (like sleep, has default cmd "sleep" in pydantic model

    primary_cmd_arg = None
    if hasattr(args, 'cmd'):
        primary_cmd_arg = args.cmd
    # Add elif for other commands here that dont have cmd? or default in pydantic model used anyways (likle sleep)

    if primary_cmd_arg is not None:
        command_input['cmd'] = primary_cmd_arg

    # Add common fields if they exist in args and are not None
    common_fields = ['only_if', 'error_if', 'error_if_not', 'loop_if', 'loop_if_not',
                     'loop_count', 'exit_on_error', 'save', 'background', 'kill_on_exit']
    for field in common_fields:
        if hasattr(args, field):
            value = getattr(args, field)
            if value is not None:
                # Convert types if necessary (e.g., loop_count to string)
                if field == 'loop_count':
                    value = str(value)
                command_input[field] = value

    # Add metadata
    if hasattr(args, 'metadata') and args.metadata:
        command_input['metadata'] = parse_key_value_pairs(args.metadata)

    # Default assumption: positional arg is 'cmd' if it exists
    if hasattr(args, 'cmd') and args.cmd is not None:
        command_input['cmd'] = args.cmd
    # Add specific fields based on command_type
    # Ensure arg names match the field names in the CommandInput Strawberry type
    specific_fields = []
    if args.command_type == 'shell':
        specific_fields = ['interactive', 'creates_session', 'session', 'command_timeout', 'read', 'command_shell', 'bin']
        if hasattr(args, 'command_timeout') and args.command_timeout is not None:
            command_input['command_timeout'] = str(args.command_timeout)  # String number
    elif args.command_type == 'sleep':
        specific_fields = ['min_sec', 'seconds', 'random']
        if hasattr(args, 'min_sec') and args.min_sec is not None:
            command_input['min_sec'] = str(args.min_sec)  # String number
        if hasattr(args, 'seconds') and args.seconds is not None:
            command_input['seconds'] = str(args.seconds)    # String number
    elif args.command_type == 'debug':
        specific_fields = ['varstore', 'exit', 'wait_for_key']
    elif args.command_type == 'setvar':
        specific_fields = ['variable', 'encoder']
        command_input['variable'] = args.variable
    elif args.command_type == 'mktemp':
        specific_fields = ['make_dir', 'variable']
        command_input['variable'] = args.variable
    #  SPECIFIC FIELDS FOR OTHER COMMANDS HERE

    for field in specific_fields:
        if hasattr(args, field):
            value = getattr(args, field)
            if value is not None:
                command_input[field] = value

    # GraphQL Mutation String
    mutation = """
        mutation ExecuteCommand($cmdInput: CommandInput!) {
            executeCommand(command: $cmdInput) {
                result {
                    success
                    stdout
                    returncode
                    errorMessage
                }
                state {
                    variables
                }
            }
        }
    """
    # convert commandInput to camelCase

    variables = {'cmdInput': convert_keys_to_camel_case(command_input)}

    try:
        logger.debug(f"Sending mutation: {mutation}")
        logger.debug(f"Variables: {json.dumps(variables, indent=2)}")
        response = client.post(server_url, json={'query': mutation, 'variables': variables})
        response.raise_for_status()
        data = response.json()
        logger.info('Received response from executeCommand.')
        logger.debug(f"Response data: {data}")

        if 'errors' in data:
            logger.error(f"GraphQL Errors: {data['errors']}")
            sys.exit(1)

        exec_response = data.get('data', {}).get('executeCommand', {})
        result = exec_response.get('result', {})
        state = exec_response.get('state', {}).get('variables', {})

        print('\n--- Command Execution Result ---')
        print(f"Success: {result.get('success')}")
        print(f"Return Code: {result.get('returncode')}")
        print(f"Stdout:\n{result.get('stdout')}")
        if result.get('errorMessage'):
            print(f"Error Message: {result.get('errorMessage')}")

        print('\n--- Updated Variable Store State ---')
        print(yaml.dump(state, indent=2, default_flow_style=False))

        is_background = hasattr(args, 'background') and args.background is True
        # Exit with error if GraphQL reports failure OR command failed (and not backgrounded)
        if not result.get('success') or (result.get('returncode') != 0 and not is_background):
            sys.exit(1)

    except httpx.RequestError as e:
        logger.error(f"HTTP Request Error executing command: {e}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error executing command: {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error executing command: {e}", exc_info=True)
        sys.exit(1)


#  TODO add more verbose help messages
def main():
    parser = argparse.ArgumentParser(description='AttackMate GraphQL Client')
    parser.add_argument('--server-url', default='http://localhost:8000/graphql', help='server endpoint URL')
    subparsers = parser.add_subparsers(dest='mode', required=True, help='Execution mode')

    # Playbook Subparser
    parser_playbook = subparsers.add_parser('playbook', help='Execute an entire playbook from a YAML file')
    parser_playbook.add_argument('playbook_file', help='Path to the playbook YAML file')

    # Remote Playbook Subparser
    parser_remote_playbook = subparsers.add_parser('remote-playbook', help='Execute an entire playbook existing on the remote machine')
    parser_remote_playbook.add_argument('playbook_file', help='Path to the playbook file on the remote machine')

    #  Command Subparser
    parser_command = subparsers.add_parser('command', help='Execute a single command')
    command_subparsers = parser_command.add_subparsers(dest='command_type', required=True, help='Specific command type')

    #  Define Common Arguments
    common_args_parser = argparse.ArgumentParser(add_help=False)
    common_args_parser.add_argument('--only-if', help='Conditional execution string')
    common_args_parser.add_argument('--error-if', help='Regex pattern for error on match')
    common_args_parser.add_argument('--error-if-not', help='Regex pattern for error if no match')
    common_args_parser.add_argument('--loop-if', help='Regex pattern to loop on match')
    common_args_parser.add_argument('--loop-if-not', help='Regex pattern to loop if no match')
    common_args_parser.add_argument('--loop-count', type=int, help='Maximum loop iterations')
    common_args_parser.add_argument('--exit-on-error', action=argparse.BooleanOptionalAction, help='Exit if command return code is non-zero')
    common_args_parser.add_argument('--save', help='File path to save command stdout')
    common_args_parser.add_argument('--background', action=argparse.BooleanOptionalAction, help='Run command in the background')
    common_args_parser.add_argument('--kill-on-exit', action=argparse.BooleanOptionalAction, help='Kill process on server exit')
    common_args_parser.add_argument('--metadata', action='append', help='Metadata key=value pair (repeatable)')

    # Subparsers for  Commands
    # Shell
    parser_shell = command_subparsers.add_parser('shell', help='Execute shell command', parents=[common_args_parser])
    parser_shell.add_argument('cmd', help='The command to execute')
    parser_shell.add_argument('--interactive', action=argparse.BooleanOptionalAction)
    parser_shell.add_argument('--creates-session', help='Name of shell session to create')
    parser_shell.add_argument('--session', help='Name of existing shell session to use')
    parser_shell.add_argument('--command-timeout', type=int)
    parser_shell.add_argument('--read', action=argparse.BooleanOptionalAction, default=True)
    parser_shell.add_argument('--command-shell', help='Shell path')
    parser_shell.add_argument('--bin', action=argparse.BooleanOptionalAction)

    # Sleep
    parser_sleep = command_subparsers.add_parser('sleep', help='Pause execution', parents=[common_args_parser])
    parser_sleep.add_argument('--seconds', type=str)
    parser_sleep.add_argument('--min-sec', type=str)
    parser_sleep.add_argument('--random', action=argparse.BooleanOptionalAction)

    # Debug
    parser_debug = command_subparsers.add_parser('debug', help='Debug output or pause', parents=[common_args_parser])
    parser_debug.add_argument('cmd', help='Message to print')
    parser_debug.add_argument('--varstore', action=argparse.BooleanOptionalAction)
    parser_debug.add_argument('--exit', action=argparse.BooleanOptionalAction)
    parser_debug.add_argument('--wait-for-key', action=argparse.BooleanOptionalAction)

    # SetVar
    parser_setvar = command_subparsers.add_parser('setvar', help='Set a variable', parents=[common_args_parser])
    parser_setvar.add_argument('cmd', help='Value to assign')
    parser_setvar.add_argument('variable', help='Name of the varibale to set')
    parser_setvar.add_argument('--encoder', help='Encoder to use')

    # Mktemp (Tempfile)
    parser_mktemp = command_subparsers.add_parser('mktemp', help='Create temporary file/directory', parents=[common_args_parser])
    parser_mktemp.add_argument('variable', help='Variable name to store the path')
    parser_mktemp.add_argument('--make-dir', action='store_true', help='Create a directory instead of a file')

    #  ADD SUBPARSERS FOR OTHER COMMANDS HERE

    args = parser.parse_args()

    #  Create HTTP Client
    timeout = httpx.Timeout(10.0, connect=5.0, read=60.0)
    client = httpx.Client(timeout=timeout)

    #  Execute
    try:
        if args.mode == 'remote-playbook':
            run_remote_playbook(client, args.server_url, args.playbook_file)
        if args.mode == 'playbook':
            run_playbook(client, args.server_url, args.playbook_file)
        elif args.mode == 'command':
            if hasattr(args, 'command_type') and args.command_type:
                run_command(client, args.server_url, args)
            else:
                logger.error('Internal error: Command mode selected but no command type subparser matched.')
                parser.print_help()
                sys.exit(1)
    finally:
        client.close()
        logger.info('HTTP client closed.')


if __name__ == '__main__':
    main()
