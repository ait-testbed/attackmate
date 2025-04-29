import grpc
import argparse
import yaml
import logging
import sys
from typing import Dict, Any

from . import common_pb2
from . import command_pb2
from . import playbook_pb2
from . import attackmate_service_pb2_grpc

from google.protobuf.json_format import MessageToDict, ParseDict

# Configure logging for the client
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLIENT - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Helper Functions


def _protobuf_to_value(pb_value: common_pb2.VariableValue) -> Any:
    """Converts a Protobuf VariableValue back to a Python value."""
    if pb_value.HasField('string_value'):
        return pb_value.string_value
    elif pb_value.HasField('number_value'):
        num = pb_value.number_value
        return int(num) if num == int(num) else num
    elif pb_value.HasField('bool_value'):
        return pb_value.bool_value
    elif pb_value.HasField('struct_value'):
        return MessageToDict(pb_value.struct_value, preserving_proto_field_name=True)
    elif pb_value.HasField('list_value'):
        # Convert ListValue back to Python list for printing
        return MessageToDict(pb_value.list_value, preserving_proto_field_name=True)
    elif pb_value.HasField('null_value'):
        return None
    return None


def _protobuf_state_to_dict(state: common_pb2.VariableStoreState) -> Dict[str, Any]:
    """Converts Protobuf VariableStoreState to a Python dictionary for display."""
    py_dict: Dict[str, common_pb2.VariableValue] = {}
    if not state:
        return py_dict
    for key, pb_value in state.variables.items():
        py_dict[key] = _protobuf_to_value(pb_value)
    return py_dict


def _parse_value(value_str: str) -> Any:
    """Attempt to parse string value into bool, int, float, or keep as string."""
    val_lower = value_str.lower()
    if val_lower in ('true', 'yes', 'y', '1'):
        return True
    if val_lower in ('false', 'no', 'n', '0'):
        return False
    try:
        return int(value_str)
    except ValueError:
        pass
    try:
        return float(value_str)
    except ValueError:
        pass
    return value_str  # Keep as string if other parsing fails ?


# Client Functions
def run_playbook(stub: attackmate_service_pb2_grpc.AttackMateServiceStub, playbook_file: str):
    """Sends a playbook YAML file to the server for execution."""
    # TODO maybe already do playbook validation client side?
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

    request = playbook_pb2.ExecutePlaybookRequest(
        playbook_yaml=playbook_yaml_content
        # TODO: Add initial_state ??
    )

    try:
        response = stub.ExecutePlaybook(request)
        logger.info('Received response from ExecutePlaybook.')

        print('\n--- Playbook Execution Result ---')
        print(f"Success: {response.success}")
        print(f"Message: {response.message}")
        print('\n--- Final Variable Store State ---')
        final_state_dict = _protobuf_state_to_dict(response.final_state)
        print(yaml.dump(final_state_dict, indent=2, default_flow_style=False))

        if not response.success:
            sys.exit(1)  # Exit with error if playbook failed

    except grpc.RpcError as e:
        logger.error(f"gRPC Error executing playbook: {e.code()} - {e.details()}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error executing playbook: {e}")
        sys.exit(1)


def run_command(stub: attackmate_service_pb2_grpc.AttackMateServiceStub, args):
    """Sends a single command to the server for execution."""
    logger.info(f"Attempting to execute command: type='{args.type}', cmd='{args.cmd}'")

    # Construct Command
    proto_command = command_pb2.Command()
    proto_command.type = args.type
    proto_command.cmd = args.cmd

    # Handle Parameters
    params_dict = {}
    if args.param:
        for p in args.param:
            if '=' not in p:
                logger.warning(f"Skipping invalid parameter format (expected key=value): {p}")
                continue
            key, value_str = p.split('=', 1)
            # Basic type parsing for the value
            params_dict[key.strip()] = _parse_value(value_str.strip())

    if params_dict:
        # Convert the Python dictionary to a Protobuf Struct
        try:
            ParseDict(params_dict, proto_command.parameters)
            logger.info(f"Parsed parameters: {params_dict}")
        except Exception as e:
            logger.error(f"Failed to parse parameters into Protobuf Struct: {e}")
            logger.error(f"Parameters attempted: {params_dict}")
            sys.exit(1)

    # Handle Common Base Command Fields
    # Only set if the argument was acctually provided by the user
    if args.only_if is not None:
        proto_command.only_if = args.only_if
    if args.error_if is not None:
        proto_command.error_if = args.error_if
    if args.error_if_not is not None:
        proto_command.error_if_not = args.error_if_not
    if args.loop_if is not None:
        proto_command.loop_if = args.loop_if
    if args.loop_if_not is not None:
        proto_command.loop_if_not = args.loop_if_not
    if args.loop_count is not None:
        proto_command.loop_count = str(args.loop_count)  # Send as string
    if args.exit_on_error is not None:
        proto_command.exit_on_error = args.exit_on_error
    if args.save is not None:
        proto_command.save = args.save
    if args.background is not None:
        proto_command.background = args.background
    if args.kill_on_exit is not None:
        proto_command.kill_on_exit = args.kill_on_exit
    # TODO Metadata handling  parsing key=value pairs?

    # Construct Request
    request = command_pb2.ExecuteCommandRequest(command=proto_command)

    try:
        response = stub.ExecuteCommand(request)
        logger.info('Received response from ExecuteCommand.')

        print('\n--- Command Execution Result ---')
        print(f"gRPC Call Success: {response.result.success}")
        print(f"Return Code: {response.result.returncode}")
        print(f"Stdout:\n{response.result.stdout}")
        if response.result.error_message:
            print(f"Error Message: {response.result.error_message}")

        print('\n--- Updated Variable Store State ---')
        updated_state_dict = _protobuf_state_to_dict(response.updated_state)
        print(yaml.dump(updated_state_dict, indent=2, default_flow_style=False))

        # Exit with error if the gRPC call reported failure OR if
        # command itself had non-zero return Code (and not background)
        if not response.result.success or (response.result.returncode != 0 and not args.background):
            sys.exit(1)

    except grpc.RpcError as e:
        logger.error(f"gRPC Error executing command: {e.code()} - {e.details()}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error executing command: {e}")
        sys.exit(1)


#  Main Execution
def main():
    parser = argparse.ArgumentParser(description='AttackMate gRPC Client')
    parser.add_argument('--server', default='localhost:50051', help='Server address (host:port)')
    subparsers = parser.add_subparsers(dest='mode', required=True, help='Execution mode')

    parser_playbook = subparsers.add_parser('playbook', help='Execute an entire playbook from a YAML file')
    parser_playbook.add_argument('playbook_file', help='Path to the playbook YAML file')

    parser_command = subparsers.add_parser('command', help='Execute a single command')
    parser_command.add_argument('type', help='The type of the command (e.g., shell, msf-module)')
    parser_command.add_argument('cmd', help='The main command string or identifier')
    # argument for command specific paramters
    parser_command.add_argument('--param', action='append', help='Command-specific parameters in key=value format (repeatable)')
    # arguments for common BaseCommand fields
    parser_command.add_argument('--only-if', help='Conditional execution string')
    parser_command.add_argument('--error-if', help='Regex pattern to cause error if stdout matches')
    parser_command.add_argument('--error-if-not', help='Regex pattern to cause error if stdout does NOT match')
    parser_command.add_argument('--loop-if', help='Regex pattern to loop if stdout matches')
    parser_command.add_argument('--loop-if-not', help='Regex pattern to loop if stdout does NOT match')
    parser_command.add_argument('--loop-count', type=int, help='Maximum loop iterations')
    parser_command.add_argument('--exit-on-error', type=bool, help='Exit if command return code is non-zero (default True)')
    parser_command.add_argument('--save', help='File path to save command stdout')
    parser_command.add_argument('--background', type=bool, help='Run command in the background (default False)')
    parser_command.add_argument('--kill-on-exit', type=bool, help='Kill background process on server exit (default True)')
    # parser_command.add_argument('--metadata', action='append', help='Metadata key=value pair (repeatable)') # TODO Needs parsing logic!!

    args = parser.parse_args()

    # Create gRPC channel and stub
    logger.info(f"Connecting to server at {args.server}...")
    try:
        # TODO secure channel in prod
        channel = grpc.insecure_channel(args.server)
        # TODO keepalive, etc. ?
        stub = attackmate_service_pb2_grpc.AttackMateServiceStub(channel)
        # Test connection, ping?
        # grpc.channel_ready_future(channel).result(timeout=5) # Example timeout
        logger.info('Channel created.')
    except Exception as e:
        logger.error(f"Failed to create gRPC channel to {args.server}: {e}")
        sys.exit(1)

    # Execute based on mode
    if args.mode == 'playbook':
        run_playbook(stub, args.playbook_file)
    elif args.mode == 'command':
        run_command(stub, args)

    # Close when done
    channel.close()
    logger.info('Channel closed.')


if __name__ == '__main__':
    main()
