# flake8: noqa
import grpc
from pydantic import ValidationError
import yaml
import logging
import traceback
from concurrent import futures
from typing import Any

from google.protobuf import struct_pb2
from google.protobuf.json_format import MessageToDict, ParseDict

from . import common_pb2, base_command_pb2, playbook_pb2, attackmate_service_pb2_grpc

from . import shell_command_pb2
from . import msf_module_command_pb2
from . import setvar_command_pb2
from . import debug_command_pb2
from . import msf_session_command_pb2
from . import ssh_command_pb2
from . import sftp_command_pb2
from . import msf_payload_command_pb2
from . import sleep_command_pb2
from . import include_command_pb2
# from . import loop_command_pb2 # TODO
from . import http_client_command_pb2
from . import webserv_command_pb2
from . import sliver_listener_command_pb2
from . import sliver_generate_command_pb2
from . import sliver_session_command_pb2
from . import father_command_pb2
from . import regex_command_pb2
from . import json_command_pb2
from . import tempfile_command_pb2
from . import vnc_command_pb2

from attackmate.schemas.shell import ShellCommand
from attackmate.schemas.metasploit import MsfModuleCommand, MsfSessionCommand, MsfPayloadCommand
from attackmate.schemas.setvar import SetVarCommand
from attackmate.schemas.debug import DebugCommand
from attackmate.schemas.ssh import SSHCommand, SFTPCommand
from attackmate.schemas.sleep import SleepCommand
from attackmate.schemas.include import IncludeCommand
# from attackmate.schemas.loop import LoopCommand # See  above
from attackmate.schemas.http import HttpClientCommand, WebServCommand
from attackmate.schemas.sliver import SliverHttpsListenerCommand, SliverGenerateCommand, SliverSessionCommand # Import base session type
from attackmate.schemas.sliver import (
    SliverSessionCDCommand, SliverSessionMKDIRCommand, SliverSessionLSCommand,
    SliverSessionDOWNLOADCommand, SliverSessionUPLOADCommand, SliverSessionNETSTATCommand,
    SliverSessionEXECCommand, SliverSessionPROCDUMPCommand, SliverSessionRMCommand,
    SliverSessionTERMINATECommand, SliverSessionSimpleCommand
)
from attackmate.schemas.father import FatherCommand
from attackmate.schemas.regex import RegExCommand
from attackmate.schemas.json import JsonCommand
from attackmate.schemas.tempfile import TempfileCommand
from attackmate.schemas.vnc import VncCommand

from attackmate.attackmate import AttackMate
from attackmate.playbook_parser import parse_config
from attackmate.schemas.playbook import Playbook
from attackmate.command import CommandRegistry
from attackmate.variablestore import VariableStore
from attackmate.logging_setup import (
    initialize_logger,
    initialize_output_logger,
    initialize_json_logger,
)
from attackmate.result import Result as AttackMateResult
from attackmate.execexception import ExecException
from attackmate.schemas.config import Config
from pydantic import ValidationError
from google.protobuf.json_format import MessageToDict, ParseDict

# Configure logging for the server
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROTO_TO_PYDANTIC_MAP = {
    # Protobuf field name : { Pydantic Class, 'type' string }
    'shell_command':          {'class': ShellCommand,          'type_str': 'shell'},
    'msf_module_command':     {'class': MsfModuleCommand,      'type_str': 'msf-module'},
    'setvar_command':         {'class': SetVarCommand,         'type_str': 'setvar'},
    'debug_command':          {'class': DebugCommand,          'type_str': 'debug'},
    'msf_session_command':    {'class': MsfSessionCommand,     'type_str': 'msf-session'},
    'ssh_command':            {'class': SSHCommand,            'type_str': 'ssh'},
    'sftp_command':           {'class': SFTPCommand,           'type_str': 'sftp'},
    'msf_payload_command':    {'class': MsfPayloadCommand,     'type_str': 'msf-payload'},
    'sleep_command':          {'class': SleepCommand,          'type_str': 'sleep'},
    'include_command':        {'class': IncludeCommand,        'type_str': 'include'},
    # "loop_command":         {"class": LoopCommand,           "type_str": "loop"}, # TODO
    'http_client_command':    {'class': HttpClientCommand,     'type_str': 'http-client'},
    'webserv_command':        {'class': WebServCommand,        'type_str': 'webserv'},
    'sliver_listener_command':{'class': SliverHttpsListenerCommand,'type_str': 'sliver'}, # Map to specific Pydantic
    'sliver_generate_command':{'class': SliverGenerateCommand,   'type_str': 'sliver'}, # Map to specific Pydantic
    'sliver_session_command': {'class': SliverSessionCommand,    'type_str': 'sliver-session'}, # Map to base, Pydantic validator handles specifics
    'father_command':         {'class': FatherCommand,         'type_str': 'father'},
    'regex_command':          {'class': RegExCommand,          'type_str': 'regex'},
    'json_command':           {'class': JsonCommand,           'type_str': 'json'},
    'tempfile_command':       {'class': TempfileCommand,       'type_str': 'mktemp'},
    'vnc_command':            {'class': VncCommand,            'type_str': 'vnc'},
    #  ADD COMMANDS HERE
}

# Helper Functions#
def _value_to_protobuf(value: Any) -> common_pb2.VariableValue:
    """Converts a Python value to a Protobuf VariableValue."""
    pb_value = common_pb2.VariableValue()
    if value is None:
        pb_value.null_value = struct_pb2.NULL_VALUE
    elif isinstance(value, bool):
        pb_value.bool_value = value
    elif isinstance(value, (int, float)):
        pb_value.number_value = value
    elif isinstance(value, str):
        pb_value.string_value = value
    elif isinstance(value, dict):
        ParseDict(value, pb_value.struct_value)
    elif isinstance(value, list):
        ParseDict(value, pb_value.list_value)
    else:
        # Fallback to string representation for unknown types
        pb_value.string_value = str(value)
        logger.warning(f"Unsupported type {type(value)} converted to string: {value}")
    return pb_value


def _protobuf_to_value(pb_value: common_pb2.VariableValue) -> Any:
    """Converts a Protobuf VariableValue back to a Python value."""
    if pb_value.HasField('string_value'):
        return pb_value.string_value
    elif pb_value.HasField('number_value'):
        # Return as int if it's a whole number, else float?
        num = pb_value.number_value
        return int(num) if num == int(num) else num
    elif pb_value.HasField('bool_value'):
        return pb_value.bool_value
    elif pb_value.HasField('struct_value'):
        return MessageToDict(pb_value.struct_value)
    elif pb_value.HasField('list_value'):
        return MessageToDict(pb_value.list_value)
    elif pb_value.HasField('null_value'):
        return None
    return None


def _varstore_to_protobuf(varstore: VariableStore) -> common_pb2.VariableStoreState:
    """Converts an AttackMate VariableStore to Protobuf VariableStoreState."""
    state = common_pb2.VariableStoreState()
    combined_vars = {}
    # string variables
    for key, value in varstore.variables.items():
        combined_vars[key] = value
    # list variables
    for key, value in varstore.lists.items():
        combined_vars[key] = value

    for key, value in combined_vars.items():
        state.variables[key].CopyFrom(_value_to_protobuf(value))

    return state


def _protobuf_to_varstore(
    state: common_pb2.VariableStoreState, varstore: VariableStore
):
    """Populates an AttackMate VariableStore from Protobuf VariableStoreState."""
    varstore.clear()
    for key, pb_value in state.variables.items():
        value = _protobuf_to_value(pb_value)
        # set_variable distinguishes between lists and strings automatically
        varstore.set_variable(key, value)

# Servicer Implementation

class AttackMateServiceImpl(attackmate_service_pb2_grpc.AttackMateServiceServicer):
    """Implements the AttackMate gRPC service."""

    def __init__(self, config: Config):
        self.config = config
        # Initialize global loggers here?
        # Initialize core AttackMate instance - THIS MAINTAINS THE STATE between ExecuteCommand calls
        # TODO  assumes thread safety --> check if this does work
        # otherwise handle requests sequentially? worker count 1?
        logger.info('Initializing persistent AttackMate instance for the server...')
        # Create a dummy initial playbook for the persistent instance
        initial_playbook = Playbook(commands=[], vars={})
        self.attackmate_instance = AttackMate(
            playbook=initial_playbook, config=self.config, varstore={}
        )
        logger.info('Persistent AttackMate instance initialized.')

    def ExecutePlaybook(
        self, request: playbook_pb2.ExecutePlaybookRequest, context
    ) -> playbook_pb2.ExecutePlaybookResponse:
        """Handles requests to execute a full playbook."""
        logger.info('Received ExecutePlaybook request.')
        response = playbook_pb2.ExecutePlaybookResponse()

        try:
            playbook_yaml_str = request.playbook_yaml
            if not playbook_yaml_str:
                raise ValueError('Playbook YAML content cannot be empty.')

            # Parse
            playbook_dict = yaml.safe_load(playbook_yaml_str)
            if not playbook_dict:
                raise ValueError('Playbook YAML not parsed successfully.')

            logger.info('Playbook YAML parsed successfully.')

            # Validate
            playbook = Playbook.model_validate(playbook_dict)
            logger.info('Playbook validated successfully.')

            # Create an AttackMate instance for this specific playbook execution -> isolated state for each full playbook run
            logger.info(
                'Creating transient AttackMate instance for playbook execution...'
            )
            initial_vars = {}
            temp_vs = VariableStore()  # Create temporary varstore to load initial state
            if request.HasField('initial_state'):
                _protobuf_to_varstore(request.initial_state, temp_vs)
                # Combine string and list vars for AttackMate constructor
                initial_vars.update(temp_vs.variables)
                initial_vars.update(temp_vs.lists)

            am_instance = AttackMate(
                playbook=playbook, config=self.config, varstore=initial_vars
            )
            logger.info('Transient AttackMate instance created.')

            # Execute  playbook
            logger.info('Executing playbook...')
            # am_instance.main() is blocking
            return_code = am_instance.main()
            logger.info(f"Playbook execution finished with code: {return_code}")

            response.success = return_code == 0
            response.message = 'Playbook execution finished.'
            response.final_state.CopyFrom(_varstore_to_protobuf(am_instance.varstore))

        except (yaml.YAMLError, ValidationError, ValueError) as e:
            error_msg = f"Error processing playbook: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response.success = False
            response.message = error_msg
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during playbook execution: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response.success = False
            response.message = error_msg
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)

        return response

    def ExecuteCommand(self, request, context) -> common_pb2.ExecutionResponse:
        logger.info('Received ExecuteCommand request (using mapping).')
        response = common_pb2.ExecutionResponse()
        response.result.success = False
        pydantic_cmd = None

        try:
            command_field = request.WhichOneof('command')
            if not command_field:
                raise ValueError('No command provided in request.')

            proto_cmd_specific = getattr(request, command_field)
            logger.info(f"Processing command type: {command_field}")

            # Look up Pydantic info from mapping
            pydantic_info = PROTO_TO_PYDANTIC_MAP.get(command_field)
            if not pydantic_info:
                raise ValueError(f"No Pydantic mapping found for proto field: {command_field}")

            PydanticClass = pydantic_info['class']
            pydantic_type_str = pydantic_info['type_str']

            # Convert proto message to dictionary
            proto_dict = MessageToDict(proto_cmd_specific, preserving_proto_field_name=True)

            # Extract and merge base fields
            # name  base field in proto is named
            base_fields = proto_dict.pop('base', {})
            if not isinstance(base_fields, dict): #  base wasn't populated
                base_fields = {}

            # Create final dict for validation
            pydantic_data = {**base_fields, **proto_dict}

            # Add the essential 'type' field required by Pydantic schemas
            pydantic_data['type'] = pydantic_type_str

            # Handle potential 'cmd' ambiguity (e.g., sliver listener/generate)
            # Pydantic class requires a specific 'cmd' value based on the type
            if pydantic_type_str == 'sliver':
                 if PydanticClass == SliverHttpsListenerCommand:
                      pydantic_data['cmd'] = 'start_https_listener'
                 elif PydanticClass == SliverGenerateCommand:
                      pydantic_data['cmd'] = 'generate_implant'
            elif pydantic_type_str == 'father':
                 pydantic_data['cmd'] = 'generate' # Implicit
            elif pydantic_type_str == 'mktemp':
                 # TODO
                 pass

            # special case: SliverSessionCommand needs specific 'cmd' based on payload TODO debug this
            if pydantic_type_str == 'sliver-session':
                payload_field = proto_cmd_specific.WhichOneof('command_payload')
                if payload_field == 'cd_payload': pydantic_data['cmd'] = 'cd'
                elif payload_field == 'mkdir_payload': pydantic_data['cmd'] = 'mkdir'
                elif payload_field == 'ls_payload': pydantic_data['cmd'] = 'ls'
                elif payload_field == 'download_payload': pydantic_data['cmd'] = 'download'
                elif payload_field == 'upload_payload': pydantic_data['cmd'] = 'upload'
                elif payload_field == 'netstat_payload': pydantic_data['cmd'] = 'netstat'
                elif payload_field == 'exec_payload': pydantic_data['cmd'] = 'execute'
                elif payload_field == 'procdump_payload': pydantic_data['cmd'] = 'process_dump'
                elif payload_field == 'rm_payload': pydantic_data['cmd'] = 'rm'
                elif payload_field == 'terminate_payload': pydantic_data['cmd'] = 'terminate'
                elif payload_field == 'ps_command': pydantic_data['cmd'] = 'ps'
                elif payload_field == 'pwd_command': pydantic_data['cmd'] = 'pwd'
                elif payload_field == 'ifconfig_command': pydantic_data['cmd'] = 'ifconfig'
                # Remove the payload structure itself
                if payload_field:
                    payload_data = pydantic_data.pop(payload_field, {})
                    pydantic_data.update(payload_data) # Merge payload fields


            logger.debug(f"Data for Pydantic validation ({PydanticClass.__name__}): {pydantic_data}")

            # Validate using Pydantic
            pydantic_cmd = PydanticClass.model_validate(pydantic_data)
            logger.info(f"Successfully converted to Pydantic: {type(pydantic_cmd).__name__}")

            # Execute command
            attackmate_result: AttackMateResult = self.attackmate_instance.run_command(pydantic_cmd)

            if attackmate_result.stdout is None and attackmate_result.returncode is None:
                response.result.success = True; response.result.stdout = 'BG/Skipped'; response.result.returncode = 0
            else:
                response.result.success = True; response.result.stdout = str(attackmate_result.stdout or ''); response.result.returncode = int(attackmate_result.returncode if attackmate_result.returncode is not None else -1)
            logger.info(f"Command execution finished. RC: {response.result.returncode}")

        except (ExecException, SystemExit) as e:
            error_msg = f"AttackMate execution error: {e}"
            logger.error(error_msg)
            response.result.success = False
            response.result.error_message = error_msg
            response.result.returncode = e.code if isinstance(e, SystemExit) and isinstance(e.code, int) else 1
        except (ValidationError, ValueError) as e:
            error_msg = f"Error processing/validating command request: {e}"
            logger.error(error_msg)
            response.result.success = False
            response.result.error_message = error_msg
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_msg)
        except Exception as e:
            error_msg = f"Unexpected server error: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response.result.success = False
            response.result.error_message = error_msg
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)


        # Populate state
        try:
            response.state.CopyFrom(_varstore_to_protobuf(self.attackmate_instance.varstore))
        except Exception as e:
            logger.error(f"Failed to get updated state: {e}")

        return response

    def cleanup(self):
        """Cleans up resources when the server shuts down."""
        logger.warning('Server shutting down. Cleaning up AttackMate instance...')
        try:
            self.attackmate_instance.clean_session_stores()
            self.attackmate_instance.pm.kill_or_wait_processes()
            logger.info('AttackMate cleanup finished.')
        except Exception as e:
            logger.error(f"Error during AttackMate cleanup: {e}")
            logger.error(traceback.format_exc())


# Server Startup

def serve():
    """Starts the gRPC server."""
    # Initialize loggers
    # configure via the main AttackMate config file?
    # TODO make configurable via command line arguments when starting up server?
    initialize_logger(debug=True, append_logs=False)
    initialize_output_logger(debug=True, append_logs=False)
    initialize_json_logger(json=True, append_logs=False)
    logger.info('AttackMate loggers initialized.')

    # Load AttackMate configuration
    # Using None for config file path, so it searches default locations
    # Pass server's logger instance
    attackmate_config = parse_config(config_file=None, logger=logger)
    logger.info('AttackMate configuration loaded.')

    # Create gRPC server
    # ThreadPoolExecutor for handling requests concurrently?
    #  max_workers=1 for sequential execution?
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Create Servicer instance
    servicer = AttackMateServiceImpl(attackmate_config)

    # Add Servicer to server
    attackmate_service_pb2_grpc.add_AttackMateServiceServicer_to_server(
        servicer, server
    )

    # Define listening port
    port = 50051
    listen_addr = f"[::]:{port}"
    # TODO secure port in production
    server.add_insecure_port(listen_addr)
    logger.info(f"Starting AttackMate gRPC server on {listen_addr}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.warning('KeyboardInterrupt received. Shutting down server...')
    finally:
        servicer.cleanup()
        server.stop(grace=5).wait()
        logger.info('Server shut down.')


if __name__ == '__main__':
    serve()
