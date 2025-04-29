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
        logger.info("Received ExecuteCommand request.")
        response = common_pb2.ExecutionResponse()
        response.result.success = False
        pydantic_cmd = None

        try:
            # which command was sent ?  get the specific proto message
            command_field = request.WhichOneof('command')
            if not command_field:
                raise ValueError("No command provided in the request.")
            proto_cmd_specific = getattr(request, command_field)
            logger.info(f"Processing command type: {command_field}")

            # Convert the  proto message to the  Pydantic model
            if command_field == "shell_command":
                pydantic_cmd = self._convert_shell_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "msf_module_command":
                pydantic_cmd = self._convert_msf_module_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "setvar_command":
                pydantic_cmd = self._convert_setvar_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "debug_command":
                pydantic_cmd = self._convert_debug_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "msf_session_command":
                pydantic_cmd = self._convert_msf_session_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "ssh_command":
                pydantic_cmd = self._convert_ssh_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "sftp_command":
                pydantic_cmd = self._convert_sftp_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "msf_payload_command":
                pydantic_cmd = self._convert_msf_payload_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "sleep_command":
                pydantic_cmd = self._convert_sleep_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "include_command":
                pydantic_cmd = self._convert_include_proto_to_pydantic(proto_cmd_specific)
            # elif command_field == "loop_command": # TODO
            #      pydantic_cmd = self._convert_loop_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "http_client_command":
                pydantic_cmd = self._convert_http_client_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "webserv_command":
                pydantic_cmd = self._convert_webserv_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "sliver_listener_command":
                pydantic_cmd = self._convert_sliver_listener_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "sliver_generate_command":
                pydantic_cmd = self._convert_sliver_generate_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "sliver_session_command":
                pydantic_cmd = self._convert_sliver_session_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "father_command":
                pydantic_cmd = self._convert_father_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "regex_command":
                pydantic_cmd = self._convert_regex_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "json_command":
                pydantic_cmd = self._convert_json_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "tempfile_command":
                pydantic_cmd = self._convert_tempfile_proto_to_pydantic(proto_cmd_specific)
            elif command_field == "vnc_command":
                pydantic_cmd = self._convert_vnc_proto_to_pydantic(proto_cmd_specific)
            else:
                raise ValueError(f"Server logic missing for command type: {command_field}")

            if pydantic_cmd is None:
                raise ValueError(f"Conversion failed for command type: {command_field}")

            logger.info(f"Converted proto to Pydantic: {type(pydantic_cmd).__name__}")

            #Execute the Pydantic command
            attackmate_result: AttackMateResult = self.attackmate_instance.run_command(pydantic_cmd)

            # Populate the response
            if attackmate_result.stdout is None and attackmate_result.returncode is None:
                response.result.success = True
                response.result.stdout = "Command likely backgrounded or skipped."
                response.result.returncode = 0
            else:
                response.result.success = True  # gRPC call succeeded
                response.result.stdout = str(attackmate_result.stdout) if attackmate_result.stdout is not None else ""
                response.result.returncode = int(attackmate_result.returncode) if attackmate_result.returncode is not None else -1

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

        # Populate the updated state
        try:
            response.state.CopyFrom(_varstore_to_protobuf(self.attackmate_instance.varstore))
        except Exception as e:
            logger.error(f"Failed to get updated variable store state after command execution: {e}")

        return response

    def _populate_base_pydantic_fields(self, pydantic_data: dict, base_proto: base_command_pb2.BaseCommandFields):
        """Copies fields from BaseCommandFields proto to a dict for Pydantic validation."""
        # Use HasField for optional fields to distinguish unset from default (e.g., false)
        # and check if the field exists in the proto definition
        if base_proto.HasField("only_if"): pydantic_data["only_if"] = base_proto.only_if
        if base_proto.HasField("error_if"): pydantic_data["error_if"] = base_proto.error_if
        if base_proto.HasField("error_if_not"): pydantic_data["error_if_not"] = base_proto.error_if_not
        if base_proto.HasField("loop_if"): pydantic_data["loop_if"] = base_proto.loop_if
        if base_proto.HasField("loop_if_not"): pydantic_data["loop_if_not"] = base_proto.loop_if_not
        if base_proto.HasField("loop_count"): pydantic_data["loop_count"] = base_proto.loop_count
        if base_proto.HasField("exit_on_error"): pydantic_data["exit_on_error"] = base_proto.exit_on_error
        if base_proto.HasField("save"): pydantic_data["save"] = base_proto.save
        if base_proto.HasField("background"): pydantic_data["background"] = base_proto.background
        if base_proto.HasField("kill_on_exit"): pydantic_data["kill_on_exit"] = base_proto.kill_on_exit
        if base_proto.metadata: pydantic_data["metadata"] = dict(base_proto.metadata) #  TODO handle metadata properly
    def _convert_shell_proto_to_pydantic(self, proto: shell_command_pb2.ShellCommandProto) -> ShellCommand:
        data = {"type": "shell"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("interactive"): data["interactive"] = proto.interactive
        if proto.HasField("creates_session"): data["creates_session"] = proto.creates_session
        if proto.HasField("session"): data["session"] = proto.session
        if proto.HasField("command_timeout"): data["command_timeout"] = proto.command_timeout
        if proto.HasField("read"): data["read"] = proto.read
        if proto.HasField("command_shell"): data["command_shell"] = proto.command_shell
        if proto.HasField("bin"): data["bin"] = proto.bin
        return ShellCommand.model_validate(data)

    def _convert_msf_module_proto_to_pydantic(self, proto: msf_module_command_pb2.MsfModuleCommandProto) -> MsfModuleCommand:
        data = {"type": "msf-module"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("target"): data["target"] = proto.target
        if proto.HasField("creates_session"): data["creates_session"] = proto.creates_session
        if proto.HasField("session"): data["session"] = proto.session
        if proto.HasField("payload"): data["payload"] = proto.payload
        if proto.options: data["options"] = dict(proto.options) # TODO handle this properly
        if proto.payload_options: data["payload_options"] = dict(proto.payload_options) # TODO handle this properly
        return MsfModuleCommand.model_validate(data)

    def _convert_setvar_proto_to_pydantic(self, proto: setvar_command_pb2.SetVarCommandProto) -> SetVarCommand:
        data = {"type": "setvar"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        data["variable"] = proto.variable
        if proto.HasField("encoder"): data["encoder"] = proto.encoder
        return SetVarCommand.model_validate(data)

    def _convert_debug_proto_to_pydantic(self, proto: debug_command_pb2.DebugCommandProto) -> DebugCommand:
        data = {"type": "debug"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("cmd"): data["cmd"] = proto.cmd
        if proto.HasField("varstore"): data["varstore"] = proto.varstore
        if proto.HasField("exit"): data["exit"] = proto.exit
        if proto.HasField("wait_for_key"): data["wait_for_key"] = proto.wait_for_key
        return DebugCommand.model_validate(data)

    def _convert_msf_session_proto_to_pydantic(self, proto: msf_session_command_pb2.MsfSessionCommandProto) -> MsfSessionCommand:
        data = {"type": "msf-session"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("stdapi"): data["stdapi"] = proto.stdapi
        if proto.HasField("write"): data["write"] = proto.write
        if proto.HasField("read"): data["read"] = proto.read
        data["session"] = proto.session
        if proto.HasField("end_str"): data["end_str"] = proto.end_str
        return MsfSessionCommand.model_validate(data)

    def _convert_ssh_proto_to_pydantic(self, proto: ssh_command_pb2.SSHCommandProto) -> SSHCommand:
        data = {"type": "ssh"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("hostname"): data["hostname"] = proto.hostname
        if proto.HasField("port"): data["port"] = proto.port
        if proto.HasField("username"): data["username"] = proto.username
        if proto.HasField("password"): data["password"] = proto.password
        if proto.HasField("passphrase"): data["passphrase"] = proto.passphrase
        if proto.HasField("key_filename"): data["key_filename"] = proto.key_filename
        if proto.HasField("creates_session"): data["creates_session"] = proto.creates_session
        if proto.HasField("session"): data["session"] = proto.session
        if proto.HasField("clear_cache"): data["clear_cache"] = proto.clear_cache
        if proto.HasField("timeout"): data["timeout"] = proto.timeout
        if proto.HasField("jmp_hostname"): data["jmp_hostname"] = proto.jmp_hostname
        if proto.HasField("jmp_port"): data["jmp_port"] = proto.jmp_port
        if proto.HasField("jmp_username"): data["jmp_username"] = proto.jmp_username
        if proto.HasField("interactive"): data["interactive"] = proto.interactive
        if proto.HasField("command_timeout"): data["command_timeout"] = proto.command_timeout
        if proto.prompts: data["prompts"] = list(proto.prompts)  # TODO fix types
        if proto.HasField("bin"): data["bin"] = proto.bin
        return SSHCommand.model_validate(data)

    def _convert_sftp_proto_to_pydantic(self, proto: sftp_command_pb2.SFTPCommandProto) -> SFTPCommand:
        data = {"type": "sftp"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("hostname"): data["hostname"] = proto.hostname
        if proto.HasField("port"): data["port"] = proto.port
        if proto.HasField("username"): data["username"] = proto.username
        if proto.HasField("password"): data["password"] = proto.password
        if proto.HasField("passphrase"): data["passphrase"] = proto.passphrase
        if proto.HasField("key_filename"): data["key_filename"] = proto.key_filename
        if proto.HasField("creates_session"): data["creates_session"] = proto.creates_session
        if proto.HasField("session"): data["session"] = proto.session
        if proto.HasField("clear_cache"): data["clear_cache"] = proto.clear_cache
        if proto.HasField("timeout"): data["timeout"] = proto.timeout
        if proto.HasField("jmp_hostname"): data["jmp_hostname"] = proto.jmp_hostname
        if proto.HasField("jmp_port"): data["jmp_port"] = proto.jmp_port
        if proto.HasField("jmp_username"): data["jmp_username"] = proto.jmp_username
        data["remote_path"] = proto.remote_path
        data["local_path"] = proto.local_path
        if proto.HasField("mode"): data["mode"] = proto.mode
        return SFTPCommand.model_validate(data)

    def _convert_msf_payload_proto_to_pydantic(self, proto: msf_payload_command_pb2.MsfPayloadCommandProto) -> MsfPayloadCommand:
        data = {"type": "msf-payload"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("format"): data["format"] = proto.format
        if proto.HasField("badchars"): data["badchars"] = proto.badchars
        if proto.HasField("force_encode"): data["force_encode"] = proto.force_encode
        if proto.HasField("encoder"): data["encoder"] = proto.encoder
        if proto.HasField("template"): data["template"] = proto.template
        if proto.HasField("platform"): data["platform"] = proto.platform
        if proto.HasField("keep_template_working"): data["keep_template_working"] = proto.keep_template_working
        if proto.HasField("nopsled_size"): data["nopsled_size"] = proto.nopsled_size
        if proto.HasField("iter"): data["iter"] = proto.iter
        if proto.payload_options: data["payload_options"] = dict(proto.payload_options) # TODO fix types
        if proto.HasField("local_path"): data["local_path"] = proto.local_path
        return MsfPayloadCommand.model_validate(data)

    def _convert_sleep_proto_to_pydantic(self, proto: sleep_command_pb2.SleepCommandProto) -> SleepCommand:
        logger.info(f"Converting sleep command")
        data = {"type": "sleep"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("cmd"): data["cmd"] = proto.cmd
        if proto.HasField("min_sec"): data["min_sec"] = proto.min_sec
        if proto.HasField("seconds"): data["seconds"] = proto.seconds
        if proto.HasField("random"): data["random"] = proto.random
        return SleepCommand.model_validate(data)

    def _convert_include_proto_to_pydantic(self, proto: include_command_pb2.IncludeCommandProto) -> IncludeCommand:
        data = {"type": "include"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("cmd"): data["cmd"] = proto.cmd
        data["local_path"] = proto.local_path
        return IncludeCommand.model_validate(data)

    # TODO LoopCommand

    def _convert_http_client_proto_to_pydantic(self, proto: http_client_command_pb2.HttpClientCommandProto) -> HttpClientCommand:
        data = {"type": "http-client"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        data["url"] = proto.url
        if proto.HasField("output_headers"): data["output_headers"] = proto.output_headers
        if proto.headers: data["headers"] = dict(proto.headers)  # TODO fix types
        if proto.cookies: data["cookies"] = dict(proto.cookies)  # TODO fix types
        if proto.data: data["data"] = dict(proto.data)  # TODO fix types
        if proto.HasField("local_path"): data["local_path"] = proto.local_path
        if proto.HasField("useragent"): data["useragent"] = proto.useragent
        if proto.HasField("follow"): data["follow"] = proto.follow
        if proto.HasField("verify"): data["verify"] = proto.verify
        if proto.HasField("http2"): data["http2"] = proto.http2
        return HttpClientCommand.model_validate(data)

    def _convert_webserv_proto_to_pydantic(self, proto: webserv_command_pb2.WebServCommandProto) -> WebServCommand:
        data = {"type": "webserv"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("cmd"): data["cmd"] = proto.cmd
        data["local_path"] = proto.local_path
        if proto.HasField("port"): data["port"] = proto.port
        if proto.HasField("address"): data["address"] = proto.address
        return WebServCommand.model_validate(data)

    def _convert_sliver_listener_proto_to_pydantic(self, proto: sliver_listener_command_pb2.SliverListenerCommandProto) -> SliverHttpsListenerCommand:
        data = {"type": "sliver", "cmd": "start_https_listener"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("host"): data["host"] = proto.host
        if proto.HasField("port"): data["port"] = proto.port
        if proto.HasField("domain"): data["domain"] = proto.domain
        if proto.HasField("website"): data["website"] = proto.website
        if proto.HasField("acme"): data["acme"] = proto.acme
        if proto.HasField("persistent"): data["persistent"] = proto.persistent
        if proto.HasField("enforce_otp"): data["enforce_otp"] = proto.enforce_otp
        if proto.HasField("randomize_jarm"): data["randomize_jarm"] = proto.randomize_jarm
        if proto.HasField("long_poll_timeout"): data["long_poll_timeout"] = proto.long_poll_timeout
        if proto.HasField("long_poll_jitter"): data["long_poll_jitter"] = proto.long_poll_jitter
        if proto.HasField("timeout"): data["timeout"] = proto.timeout
        return SliverHttpsListenerCommand.model_validate(data)

    def _convert_sliver_generate_proto_to_pydantic(self, proto: sliver_generate_command_pb2.SliverGenerateCommandProto) -> SliverGenerateCommand:
        data = {"type": "sliver", "cmd": "generate_implant"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("target"): data["target"] = proto.target
        data["c2url"] = proto.c2url
        if proto.HasField("format"): data["format"] = proto.format
        data["name"] = proto.name
        if proto.HasField("filepath"): data["filepath"] = proto.filepath
        if proto.HasField("IsBeacon"): data["IsBeacon"] = proto.IsBeacon
        if proto.HasField("BeaconInterval"): data["BeaconInterval"] = proto.BeaconInterval
        if proto.HasField("RunAtLoad"): data["RunAtLoad"] = proto.RunAtLoad
        if proto.HasField("Evasion"): data["Evasion"] = proto.Evasion
        return SliverGenerateCommand.model_validate(data)

    # TODO debug all of this
    def _convert_sliver_session_proto_to_pydantic(self, proto: sliver_session_command_pb2.SliverSessionCommandProto) -> SliverSessionCommand:
        #  specific Pydantic class depends on the 'oneof' payload
        data = {"type": "sliver-session"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["session"] = proto.session
        if proto.HasField("beacon"): data["beacon"] = proto.beacon

        payload_field = proto.WhichOneof('command_payload')
        if not payload_field:
            raise ValueError("SliverSessionCommandProto missing specific command payload")

        PydanticClass = None
        if payload_field == "cd_payload":
            data["cmd"] = "cd"
            PydanticClass = SliverSessionCDCommand
            pl = proto.cd_payload
            data["remote_path"] = pl.remote_path
        elif payload_field == "mkdir_payload":
             data["cmd"] = "mkdir"
             PydanticClass = SliverSessionMKDIRCommand
             pl = proto.mkdir_payload
             data["remote_path"] = pl.remote_path
        elif payload_field == "ls_payload":
            data["cmd"] = "ls"
            PydanticClass = SliverSessionLSCommand
            pl = proto.ls_payload
            data["remote_path"] = pl.remote_path
        elif payload_field == "download_payload":
            data["cmd"] = "download"
            PydanticClass = SliverSessionDOWNLOADCommand
            pl = proto.download_payload
            data["remote_path"] = pl.remote_path
            if pl.HasField("local_path"): data["local_path"] = pl.local_path
            if pl.HasField("recurse"): data["recurse"] = pl.recurse
        elif payload_field == "upload_payload":
            data["cmd"] = "upload"
            PydanticClass = SliverSessionUPLOADCommand
            pl = proto.upload_payload
            data["remote_path"] = pl.remote_path
            if pl.HasField("local_path"): data["local_path"] = pl.local_path
            if pl.HasField("is_ioc"): data["is_ioc"] = pl.is_ioc
        elif payload_field == "netstat_payload":
            data["cmd"] = "netstat"
            PydanticClass = SliverSessionNETSTATCommand
            pl = proto.netstat_payload
            if pl.HasField("tcp"): data["tcp"] = pl.tcp
            if pl.HasField("udp"): data["udp"] = pl.udp
            if pl.HasField("ipv4"): data["ipv4"] = pl.ipv4
            if pl.HasField("ipv6"): data["ipv6"] = pl.ipv6
            if pl.HasField("listening"): data["listening"] = pl.listening
        elif payload_field == "exec_payload":
            data["cmd"] = "execute"
            PydanticClass = SliverSessionEXECCommand
            pl = proto.exec_payload
            data["exe"] = pl.exe
            if pl.args: data["args"] = list(pl.args)   # TODO fix types
            if pl.HasField("output"): data["output"] = pl.output
        elif payload_field == "procdump_payload":
            data["cmd"] = "process_dump"
            PydanticClass = SliverSessionPROCDUMPCommand
            pl = proto.procdump_payload
            data["local_path"] = pl.local_path
            data["pid"] = pl.pid
        elif payload_field == "rm_payload":
            data["cmd"] = "rm"
            PydanticClass = SliverSessionRMCommand
            pl = proto.rm_payload
            data["remote_path"] = pl.remote_path
            if pl.HasField("recursive"): data["recursive"] = pl.recursive
            if pl.HasField("force"): data["force"] = pl.force
        elif payload_field == "terminate_payload":
            data["cmd"] = "terminate"
            PydanticClass = SliverSessionTERMINATECommand
            pl = proto.terminate_payload
            data["pid"] = pl.pid
            if pl.HasField("force"): data["force"] = pl.force
        elif payload_field == "ps_command" and proto.ps_command:
             data["cmd"] = "ps"
             PydanticClass = SliverSessionSimpleCommand
        elif payload_field == "pwd_command" and proto.pwd_command:
             data["cmd"] = "pwd"
             PydanticClass = SliverSessionSimpleCommand
        elif payload_field == "ifconfig_command" and proto.ifconfig_command:
             data["cmd"] = "ifconfig"
             PydanticClass = SliverSessionSimpleCommand
        else:
            raise ValueError(f"Unknown or unhandled sliver session payload type: {payload_field}")

        if PydanticClass is None:
             raise ValueError(f"Could not determine Pydantic class for sliver session payload: {payload_field}")

        return PydanticClass.model_validate(data)

    def _convert_father_proto_to_pydantic(self, proto: father_command_pb2.FatherCommandProto) -> FatherCommand:
        data = {"type": "father", "cmd": "generate"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("gid"): data["gid"] = proto.gid
        if proto.HasField("srcport"): data["srcport"] = proto.srcport
        if proto.HasField("epochtime"): data["epochtime"] = proto.epochtime
        if proto.HasField("env_var"): data["env_var"] = proto.env_var
        if proto.HasField("file_prefix"): data["file_prefix"] = proto.file_prefix
        if proto.HasField("preload_file"): data["preload_file"] = proto.preload_file
        if proto.HasField("hiddenport"): data["hiddenport"] = proto.hiddenport
        if proto.HasField("shell_pass"): data["shell_pass"] = proto.shell_pass
        if proto.HasField("install_path"): data["install_path"] = proto.install_path
        if proto.HasField("local_path"): data["local_path"] = proto.local_path
        if proto.HasField("arch"): data["arch"] = proto.arch
        if proto.HasField("build_command"): data["build_command"] = proto.build_command
        return FatherCommand.model_validate(data)

    def _convert_regex_proto_to_pydantic(self, proto: regex_command_pb2.RegExCommandProto) -> RegExCommand:
        data = {"type": "regex"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("replace"): data["replace"] = proto.replace
        if proto.HasField("mode"): data["mode"] = proto.mode
        if proto.HasField("input"): data["input"] = proto.input
        if proto.output: data["output"] = dict(proto.output)  # TODO fix types
        return RegExCommand.model_validate(data)

    def _convert_json_proto_to_pydantic(self, proto: json_command_pb2.JsonCommandProto) -> JsonCommand:
        data = {"type": "json"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("cmd"): data["cmd"] = proto.cmd
        if proto.HasField("local_path"): data["local_path"] = proto.local_path
        if proto.HasField("varstore"): data["varstore"] = proto.varstore
        return JsonCommand.model_validate(data)

    def _convert_tempfile_proto_to_pydantic(self, proto: tempfile_command_pb2.TempfileCommandProto) -> TempfileCommand:
        data = {"type": "mktemp"}
        self._populate_base_pydantic_fields(data, proto.base)
        if proto.HasField("cmd"): data["cmd"] = proto.cmd
        data["variable"] = proto.variable
        return TempfileCommand.model_validate(data)

    def _convert_vnc_proto_to_pydantic(self, proto: vnc_command_pb2.VncCommandProto) -> VncCommand:
        data = {"type": "vnc"}
        self._populate_base_pydantic_fields(data, proto.base)
        data["cmd"] = proto.cmd
        if proto.HasField("hostname"): data["hostname"] = proto.hostname
        if proto.HasField("port"): data["port"] = proto.port
        if proto.HasField("display"): data["display"] = proto.display
        if proto.HasField("password"): data["password"] = proto.password
        if proto.HasField("key"): data["key"] = proto.key
        if proto.HasField("input"): data["input"] = proto.input
        if proto.HasField("filename"): data["filename"] = proto.filename
        if proto.HasField("x"): data["x"] = proto.x
        if proto.HasField("y"): data["y"] = proto.y
        if proto.HasField("creates_session"): data["creates_session"] = proto.creates_session
        if proto.HasField("session"): data["session"] = proto.session
        if proto.HasField("maxrms"): data["maxrms"] = proto.maxrms
        if proto.HasField("expect_timeout"): data["expect_timeout"] = proto.expect_timeout
        if proto.HasField("connection_timeout"): data["connection_timeout"] = proto.connection_timeout
        return VncCommand.model_validate(data)

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
