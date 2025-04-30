# flake8: noqa
import traceback
import grpc
import argparse
import yaml
import logging
import sys
from typing import Dict, Any, List

from . import common_pb2
from . import base_command_pb2
from . import playbook_pb2
from . import attackmate_service_pb2_grpc
from . import attackmate_service_pb2

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
from attackmate.schemas.sliver import SliverHttpsListenerCommand, SliverGenerateCommand, SliverSessionCommand
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

from google.protobuf.json_format import MessageToDict, ParseDict

# Configure logging for the client
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLIENT - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Helper Functions

# # mapping to reduce code duplication
# COMMAND_TYPE_TO_PROTO_CLASS = {
#     "shell": shell_command_pb2.ShellCommandProto,
#     "msf-module": msf_module_command_pb2.MsfModuleCommandProto,
#     "setvar": setvar_command_pb2.SetVarCommandProto,
#     "debug": debug_command_pb2.DebugCommandProto,
#     "msf-session": msf_session_command_pb2.MsfSessionCommandProto,
#     "ssh": ssh_command_pb2.SSHCommandProto,
#     "sftp": sftp_command_pb2.SFTPCommandProto,
#     "msf-payload": msf_payload_command_pb2.MsfPayloadCommandProto,
#     "sleep": sleep_command_pb2.SleepCommandProto,
#     "include": include_command_pb2.IncludeCommandProto,
#     # "loop": loop_command_pb2.LoopCommandProto, # If adding later
#     "http-client": http_client_command_pb2.HttpClientCommandProto,
#     "webserv": webserv_command_pb2.WebServCommandProto,
#     "sliver-listener": sliver_listener_command_pb2.SliverListenerCommandProto,
#     "sliver-generate": sliver_generate_command_pb2.SliverGenerateCommandProto,
#     "sliver-session": sliver_session_command_pb2.SliverSessionCommandProto,
#     "father": father_command_pb2.FatherCommandProto,
#     "regex": regex_command_pb2.RegExCommandProto,
#     "json": json_command_pb2.JsonCommandProto,
#     "tempfile": tempfile_command_pb2.TempfileCommandProto,
#     "vnc": vnc_command_pb2.VncCommandProto,
#     # ADD OTHERS HERE
# }


def _protobuf_to_value(pb_value: common_pb2.VariableValue) -> Any:
    if pb_value.HasField("string_value"): return pb_value.string_value
    elif pb_value.HasField("number_value"): num = pb_value.number_value; return int(num) if num == int(num) else num
    elif pb_value.HasField("bool_value"): return pb_value.bool_value
    elif pb_value.HasField("struct_value"): return MessageToDict(pb_value.struct_value)
    elif pb_value.HasField("list_value"): return MessageToDict(pb_value.list_value)
    elif pb_value.HasField("null_value"): return None
    return None


def _protobuf_state_to_dict(state: common_pb2.VariableStoreState) -> Dict[str, Any]:
    """Converts Protobuf VariableStoreState to a Python dictionary for display."""
    py_dict: Dict[str, common_pb2.VariableValue] = {}
    if not state:
        return py_dict
    for key, pb_value in state.variables.items():
        py_dict[key] = _protobuf_to_value(pb_value)
    return py_dict

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
            logger.warning(f"Skipping malformed key-value pair (expected key=value): {item}")
    return result

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

def populate_base_proto_fields(base_proto: base_command_pb2.BaseCommandFields, args: argparse.Namespace):
    """Populates BaseCommandFields proto from parsed arguments."""
    # Check if attribute exists in args before accessing (important with subparsers)
    if hasattr(args, 'only_if') and args.only_if is not None: base_proto.only_if = args.only_if
    if hasattr(args, 'error_if') and args.error_if is not None: base_proto.error_if = args.error_if
    if hasattr(args, 'error_if_not') and args.error_if_not is not None: base_proto.error_if_not = args.error_if_not
    if hasattr(args, 'loop_if') and args.loop_if is not None: base_proto.loop_if = args.loop_if
    if hasattr(args, 'loop_if_not') and args.loop_if_not is not None: base_proto.loop_if_not = args.loop_if_not
    if hasattr(args, 'loop_count') and args.loop_count is not None: base_proto.loop_count = str(args.loop_count)
    if hasattr(args, 'exit_on_error') and args.exit_on_error is not None: base_proto.exit_on_error = args.exit_on_error
    if hasattr(args, 'save') and args.save is not None: base_proto.save = args.save
    if hasattr(args, 'background') and args.background is not None: base_proto.background = args.background
    if hasattr(args, 'kill_on_exit') and args.kill_on_exit is not None: base_proto.kill_on_exit = args.kill_on_exit
    if hasattr(args, 'metadata') and args.metadata:
         metadata_dict = parse_key_value_pairs(args.metadata)
         base_proto.metadata.update(metadata_dict)

def run_command(stub: attackmate_service_pb2_grpc.AttackMateServiceStub, args):
    """Sends a specific command type to the server."""
    logger.info(f"Attempting to execute command: type='{args.command_type}'")

    # Use the correct Request type
    request = attackmate_service_pb2.ExecuteCommandRequest()
    command_type = args.command_type # Use the subparser dest directly

    try:
        # --- Construct the specific command proto based on args.command_type ---
        if command_type == "shell":
            proto_cmd = shell_command_pb2.ShellCommandProto()
            populate_base_proto_fields(proto_cmd.base, args)
            proto_cmd.cmd = args.cmd_string
            if args.interactive is not None: proto_cmd.interactive = args.interactive
            if args.creates_session is not None: proto_cmd.creates_session = args.creates_session
            if args.session is not None: proto_cmd.session = args.session
            if args.command_timeout is not None: proto_cmd.command_timeout = str(args.command_timeout)
            if args.read is not None: proto_cmd.read = args.read
            if args.command_shell is not None: proto_cmd.command_shell = args.command_shell
            if args.bin is not None: proto_cmd.bin = args.bin
            request.shell_command.CopyFrom(proto_cmd)

        elif command_type == "msf-module":
            proto_cmd = msf_module_command_pb2.MsfModuleCommandProto()
            populate_base_proto_fields(proto_cmd.base, args)
            proto_cmd.cmd = args.cmd_string # Module path
            if args.target is not None: proto_cmd.target = str(args.target)
            if args.creates_session is not None: proto_cmd.creates_session = args.creates_session
            if args.session is not None: proto_cmd.session = args.session
            if args.payload is not None: proto_cmd.payload = args.payload
            if args.option: proto_cmd.options.update(parse_key_value_pairs(args.option))
            if args.payload_option: proto_cmd.payload_options.update(parse_key_value_pairs(args.payload_option))
            request.msf_module_command.CopyFrom(proto_cmd)

        elif command_type == "setvar":
             proto_cmd = setvar_command_pb2.SetVarCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.variable = args.variable_name
             proto_cmd.cmd = args.value_string # Value to set
             if args.encoder is not None: proto_cmd.encoder = args.encoder
             request.setvar_command.CopyFrom(proto_cmd)

        elif command_type == "debug":
             proto_cmd = debug_command_pb2.DebugCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             if args.message is not None: proto_cmd.cmd = args.message
             if args.varstore is not None: proto_cmd.varstore = args.varstore
             if args.exit is not None: proto_cmd.exit = args.exit
             if args.wait_for_key is not None: proto_cmd.wait_for_key = args.wait_for_key
             request.debug_command.CopyFrom(proto_cmd)

        elif command_type == "msf-session":
             proto_cmd = msf_session_command_pb2.MsfSessionCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.cmd = args.cmd_string # Command to run/write
             proto_cmd.session = args.session_name
             if args.stdapi is not None: proto_cmd.stdapi = args.stdapi
             if args.write is not None: proto_cmd.write = args.write
             if args.read is not None: proto_cmd.read = args.read
             if args.end_str is not None: proto_cmd.end_str = args.end_str
             request.msf_session_command.CopyFrom(proto_cmd)

        elif command_type == "ssh":
             proto_cmd = ssh_command_pb2.SSHCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.cmd = args.cmd_string
             if args.hostname is not None: proto_cmd.hostname = args.hostname
             if args.port is not None: proto_cmd.port = str(args.port)
             if args.username is not None: proto_cmd.username = args.username
             if args.password is not None: proto_cmd.password = args.password
             if args.passphrase is not None: proto_cmd.passphrase = args.passphrase
             if args.key_filename is not None: proto_cmd.key_filename = args.key_filename
             if args.creates_session is not None: proto_cmd.creates_session = args.creates_session
             if args.session is not None: proto_cmd.session = args.session
             if args.clear_cache is not None: proto_cmd.clear_cache = args.clear_cache
             if args.timeout is not None: proto_cmd.timeout = float(args.timeout)
             if args.jmp_hostname is not None: proto_cmd.jmp_hostname = args.jmp_hostname
             if args.jmp_port is not None: proto_cmd.jmp_port = str(args.jmp_port)
             if args.jmp_username is not None: proto_cmd.jmp_username = args.jmp_username
             if args.interactive is not None: proto_cmd.interactive = args.interactive
             if args.command_timeout is not None: proto_cmd.command_timeout = str(args.command_timeout)
             if args.prompts: proto_cmd.prompts.extend(args.prompts)
             if args.bin is not None: proto_cmd.bin = args.bin
             request.ssh_command.CopyFrom(proto_cmd)

        elif command_type == "sftp":
             proto_cmd = sftp_command_pb2.SFTPCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.cmd = args.sftp_action # 'get' or 'put'
             proto_cmd.remote_path = args.remote_path
             proto_cmd.local_path = args.local_path
             if args.hostname is not None: proto_cmd.hostname = args.hostname
             if args.port is not None: proto_cmd.port = str(args.port)
             if args.username is not None: proto_cmd.username = args.username
             if args.password is not None: proto_cmd.password = args.password
             if args.passphrase is not None: proto_cmd.passphrase = args.passphrase
             if args.key_filename is not None: proto_cmd.key_filename = args.key_filename
             if args.creates_session is not None: proto_cmd.creates_session = args.creates_session
             if args.session is not None: proto_cmd.session = args.session
             if args.clear_cache is not None: proto_cmd.clear_cache = args.clear_cache
             if args.timeout is not None: proto_cmd.timeout = float(args.timeout)
             if args.jmp_hostname is not None: proto_cmd.jmp_hostname = args.jmp_hostname
             if args.jmp_port is not None: proto_cmd.jmp_port = str(args.jmp_port)
             if args.jmp_username is not None: proto_cmd.jmp_username = args.jmp_username
             if args.mode is not None: proto_cmd.mode = args.mode
             request.sftp_command.CopyFrom(proto_cmd)

        elif command_type == "msf-payload":
             proto_cmd = msf_payload_command_pb2.MsfPayloadCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.cmd = args.payload_path # Payload path (e.g., windows/...)
             if args.format is not None: proto_cmd.format = args.format
             if args.badchars is not None: proto_cmd.badchars = args.badchars
             if args.force_encode is not None: proto_cmd.force_encode = args.force_encode
             if args.encoder is not None: proto_cmd.encoder = args.encoder
             if args.template is not None: proto_cmd.template = args.template
             if args.platform is not None: proto_cmd.platform = args.platform
             if args.keep_template_working is not None: proto_cmd.keep_template_working = args.keep_template_working
             if args.nopsled_size is not None: proto_cmd.nopsled_size = str(args.nopsled_size)
             if args.iter is not None: proto_cmd.iter = str(args.iter)
             if args.payload_option: proto_cmd.payload_options.update(parse_key_value_pairs(args.payload_option))
             if args.local_path is not None: proto_cmd.local_path = args.local_path
             request.msf_payload_command.CopyFrom(proto_cmd)

        elif command_type == "sleep":
             proto_cmd = sleep_command_pb2.SleepCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             # cmd is optional for sleep, default handled server-side
             if args.min_sec is not None: proto_cmd.min_sec = str(args.min_sec)
             if args.seconds is not None: proto_cmd.seconds = str(args.seconds)
             if args.random is not None: proto_cmd.random = args.random
             request.sleep_command.CopyFrom(proto_cmd)

        elif command_type == "include":
             proto_cmd = include_command_pb2.IncludeCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.local_path = args.include_file_path
             # cmd is optional for include, default handled server-side
             request.include_command.CopyFrom(proto_cmd)

        elif command_type == "http-client":
             proto_cmd = http_client_command_pb2.HttpClientCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.cmd = args.method # GET, POST, etc.
             proto_cmd.url = args.url
             if args.output_headers is not None: proto_cmd.output_headers = args.output_headers
             if args.header: proto_cmd.headers.update(parse_key_value_pairs(args.header))
             if args.cookie: proto_cmd.cookies.update(parse_key_value_pairs(args.cookie))
             if args.data: proto_cmd.data.update(parse_key_value_pairs(args.data))
             if args.local_path is not None: proto_cmd.local_path = args.local_path
             if args.useragent is not None: proto_cmd.useragent = args.useragent
             if args.follow is not None: proto_cmd.follow = args.follow
             if args.verify is not None: proto_cmd.verify = args.verify
             if args.http2 is not None: proto_cmd.http2 = args.http2
             request.http_client_command.CopyFrom(proto_cmd)

        elif command_type == "webserv":
             proto_cmd = webserv_command_pb2.WebServCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.local_path = args.file_to_serve
             if args.port is not None: proto_cmd.port = str(args.port)
             if args.address is not None: proto_cmd.address = args.address
             # cmd is optional for webserv, default handled server-side
             request.webserv_command.CopyFrom(proto_cmd)

        elif command_type == "sliver-listener": # Maps to start_https_listener implicitly
             proto_cmd = sliver_listener_command_pb2.SliverListenerCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             if args.host is not None: proto_cmd.host = args.host
             if args.port is not None: proto_cmd.port = str(args.port)
             if args.domain is not None: proto_cmd.domain = args.domain
             if args.website is not None: proto_cmd.website = args.website
             if args.acme is not None: proto_cmd.acme = args.acme
             if args.persistent is not None: proto_cmd.persistent = args.persistent
             if args.enforce_otp is not None: proto_cmd.enforce_otp = args.enforce_otp
             if args.randomize_jarm is not None: proto_cmd.randomize_jarm = args.randomize_jarm
             if args.long_poll_timeout is not None: proto_cmd.long_poll_timeout = str(args.long_poll_timeout)
             if args.long_poll_jitter is not None: proto_cmd.long_poll_jitter = str(args.long_poll_jitter)
             if args.timeout is not None: proto_cmd.timeout = str(args.timeout)
             request.sliver_listener_command.CopyFrom(proto_cmd)

        elif command_type == "sliver-generate": # Maps to generate_implant implicitly
             proto_cmd = sliver_generate_command_pb2.SliverGenerateCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.c2url = args.c2url
             proto_cmd.name = args.implant_name
             if args.target is not None: proto_cmd.target = args.target
             if args.format is not None: proto_cmd.format = args.format
             if args.filepath is not None: proto_cmd.filepath = args.filepath
             if args.is_beacon is not None: proto_cmd.IsBeacon = args.is_beacon
             if args.beacon_interval is not None: proto_cmd.BeaconInterval = str(args.beacon_interval)
             if args.run_at_load is not None: proto_cmd.RunAtLoad = args.run_at_load
             if args.evasion is not None: proto_cmd.Evasion = args.evasion
             request.sliver_generate_command.CopyFrom(proto_cmd)

        elif command_type == "sliver-session":
            proto_cmd = sliver_session_command_pb2.SliverSessionCommandProto()
            populate_base_proto_fields(proto_cmd.base, args)
            proto_cmd.session = args.session_name
            if args.beacon is not None: proto_cmd.beacon = args.beacon

            # Determine which sub-command payload to set
            sub_cmd = args.sliver_sub_cmd.lower()
            if sub_cmd == 'cd':
                 proto_cmd.cd_payload.remote_path = args.remote_path
            elif sub_cmd == 'mkdir':
                 proto_cmd.mkdir_payload.remote_path = args.remote_path
            elif sub_cmd == 'ls':
                 proto_cmd.ls_payload.remote_path = args.remote_path
            elif sub_cmd == 'download':
                 proto_cmd.download_payload.remote_path = args.remote_path
                 if args.local_path is not None: proto_cmd.download_payload.local_path = args.local_path
                 if args.recurse is not None: proto_cmd.download_payload.recurse = args.recurse
            elif sub_cmd == 'upload':
                proto_cmd.upload_payload.remote_path = args.remote_path
                if args.local_path is not None: proto_cmd.upload_payload.local_path = args.local_path
                if args.is_ioc is not None: proto_cmd.upload_payload.is_ioc = args.is_ioc
            elif sub_cmd == 'netstat':
                if args.tcp is not None: proto_cmd.netstat_payload.tcp = args.tcp
                if args.udp is not None: proto_cmd.netstat_payload.udp = args.udp
                if args.ipv4 is not None: proto_cmd.netstat_payload.ipv4 = args.ipv4
                if args.ipv6 is not None: proto_cmd.netstat_payload.ipv6 = args.ipv6
                if args.listening is not None: proto_cmd.netstat_payload.listening = args.listening
            elif sub_cmd == 'execute':
                proto_cmd.exec_payload.exe = args.exe_path
                if args.args: proto_cmd.exec_payload.args.extend(args.args)
                if args.output is not None: proto_cmd.exec_payload.output = args.output
            elif sub_cmd == 'process_dump':
                 proto_cmd.procdump_payload.local_path = args.local_path
                 proto_cmd.procdump_payload.pid = str(args.pid)
            elif sub_cmd == 'rm':
                 proto_cmd.rm_payload.remote_path = args.remote_path
                 if args.recursive is not None: proto_cmd.rm_payload.recursive = args.recursive
                 if args.force is not None: proto_cmd.rm_payload.force = args.force
            elif sub_cmd == 'terminate':
                 proto_cmd.terminate_payload.pid = str(args.pid)
                 if args.force is not None: proto_cmd.terminate_payload.force = args.force
            elif sub_cmd == 'ps':
                 proto_cmd.ps_command = True
            elif sub_cmd == 'pwd':
                 proto_cmd.pwd_command = True
            elif sub_cmd == 'ifconfig':
                 proto_cmd.ifconfig_command = True
            else:
                 raise ValueError(f"Unknown sliver-session sub-command: {sub_cmd}")
            request.sliver_session_command.CopyFrom(proto_cmd)

        elif command_type == "father":
             proto_cmd = father_command_pb2.FatherCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             if args.gid is not None: proto_cmd.gid = args.gid
             if args.srcport is not None: proto_cmd.srcport = args.srcport
             if args.epochtime is not None: proto_cmd.epochtime = args.epochtime
             if args.env_var is not None: proto_cmd.env_var = args.env_var
             if args.file_prefix is not None: proto_cmd.file_prefix = args.file_prefix
             if args.preload_file is not None: proto_cmd.preload_file = args.preload_file
             if args.hiddenport is not None: proto_cmd.hiddenport = args.hiddenport
             if args.shell_pass is not None: proto_cmd.shell_pass = args.shell_pass
             if args.install_path is not None: proto_cmd.install_path = args.install_path
             if args.local_path is not None: proto_cmd.local_path = args.local_path
             if args.arch is not None: proto_cmd.arch = args.arch
             if args.build_command is not None: proto_cmd.build_command = args.build_command
             request.father_command.CopyFrom(proto_cmd)

        elif command_type == "regex":
             proto_cmd = regex_command_pb2.RegExCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.cmd = args.pattern
             if args.replace is not None: proto_cmd.replace = args.replace
             if args.mode is not None: proto_cmd.mode = args.mode
             if args.input_var is not None: proto_cmd.input = args.input_var
             if args.output_map: proto_cmd.output.update(parse_key_value_pairs(args.output_map))
             request.regex_command.CopyFrom(proto_cmd)

        elif command_type == "json":
             proto_cmd = json_command_pb2.JsonCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             if args.cmd_var is not None: proto_cmd.cmd = args.cmd_var
             if args.local_path is not None: proto_cmd.local_path = args.local_path
             if args.log_varstore is not None: proto_cmd.varstore = args.log_varstore
             request.json_command.CopyFrom(proto_cmd)

        elif command_type == "tempfile":
             proto_cmd = tempfile_command_pb2.TempfileCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.variable = args.variable_name
             if args.make_dir: proto_cmd.cmd = "dir"
             else: proto_cmd.cmd = "file"
             request.tempfile_command.CopyFrom(proto_cmd)

        elif command_type == "vnc":
             proto_cmd = vnc_command_pb2.VncCommandProto()
             populate_base_proto_fields(proto_cmd.base, args)
             proto_cmd.cmd = args.vnc_action
             if args.hostname is not None: proto_cmd.hostname = args.hostname
             if args.port is not None: proto_cmd.port = str(args.port)
             if args.display is not None: proto_cmd.display = str(args.display)
             if args.password is not None: proto_cmd.password = args.password
             if args.key is not None: proto_cmd.key = args.key
             if args.input_str is not None: proto_cmd.input = args.input_str
             if args.filename is not None: proto_cmd.filename = args.filename
             if args.x is not None: proto_cmd.x = args.x
             if args.y is not None: proto_cmd.y = args.y
             if args.creates_session is not None: proto_cmd.creates_session = args.creates_session
             if args.session is not None: proto_cmd.session = args.session
             if args.maxrms is not None: proto_cmd.maxrms = args.maxrms
             if args.expect_timeout is not None: proto_cmd.expect_timeout = args.expect_timeout
             if args.connection_timeout is not None: proto_cmd.connection_timeout = args.connection_timeout
             request.vnc_command.CopyFrom(proto_cmd)

        else:
            # should not happen if all subparsers are defined
            logger.error(f"Client doesn't know how to construct command type: {command_type}")
            sys.exit(1)

    except AttributeError as e:
         logger.error(f"Error accessing arguments for command '{command_type}', check command line structure and parser definition: {e}")
         sys.exit(1)
    except ValueError as e:
         logger.error(f"Error constructing command '{command_type}': {e}")
         sys.exit(1)


    #  Send Request and Handle Response
    try:
        # Response type is common_pb2.ExecutionResponse
        response = stub.ExecuteCommand(request)
        logger.info("Received response from ExecuteCommand.")

        print("\n--- Command Execution Result ---")
        print(f"Success: {response.result.success}")
        print(f"Return Code: {response.result.returncode}")
        print(f"Stdout:\n{response.result.stdout}")
        if response.result.error_message:
            print(f"Error Message: {response.result.error_message}")

        print("\n--- Updated Variable Store State ---")
        updated_state_dict = _protobuf_state_to_dict(response.state)
        print(yaml.dump(updated_state_dict, indent=2, default_flow_style=False))
        print("-" * 30)

        # Check if base 'background' arg exists and is True
        is_background = hasattr(args, 'background') and args.background is True
        if not response.result.success or (response.result.returncode != 0 and not is_background):
             sys.exit(1)

    except grpc.RpcError as e:
        logger.error(f"gRPC Error: {e.code()} - {e.details()}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


#  Main Execution
def main():
    parser = argparse.ArgumentParser(description="AttackMate gRPC Client (Specific Commands)")
    parser.add_argument('--server', default='localhost:50051', help='Server address (host:port)')
    subparsers = parser.add_subparsers(dest='mode', required=True, help='Execution mode')

    #  Playbook Subparser
    parser_playbook = subparsers.add_parser('playbook', help='Execute an entire playbook from a YAML file')
    parser_playbook.add_argument('playbook_file', help='Path to the playbook YAML file')

    #  Command Subparser
    parser_command = subparsers.add_parser('command', help='Execute a single command')
    command_subparsers = parser_command.add_subparsers(dest='command_type', required=True, help='Specific command type')

    #  Define Common Arguments Once
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
    common_args_parser.add_argument('--kill-on-exit', action=argparse.BooleanOptionalAction, help='Kill background process on server exit')

    # common_args_parser.add_argument('--metadata', action='append', help='Metadata key=value pair (repeatable)') # TODO Needs parsing logic


    #  Shell Command Arguments
    parser_shell = command_subparsers.add_parser('shell', help='Execute shell command', parents=[common_args_parser])
    parser_shell.add_argument('cmd_string', help='The command to execute')
    parser_shell.add_argument('--interactive', action=argparse.BooleanOptionalAction, help='Run interactively')
    parser_shell.add_argument('--creates-session', help='Name of shell session to create')
    parser_shell.add_argument('--session', help='Name of existing shell session to use')
    parser_shell.add_argument('--command-timeout', type=int, help='Timeout for interactive command read')
    parser_shell.add_argument('--read', action=argparse.BooleanOptionalAction, default=True, help='Read output in interactive mode')
    parser_shell.add_argument('--command-shell', help='Shell path (e.g., /bin/bash)')
    parser_shell.add_argument('--bin', action=argparse.BooleanOptionalAction, help='Send command as hex binary')

    #  MsfModule Command Arguments
    parser_msf_module = command_subparsers.add_parser('msf-module', help='Execute a Metasploit module', parents=[common_args_parser])
    parser_msf_module.add_argument('cmd_string', help='Module path (e.g., exploit/...)')
    parser_msf_module.add_argument('--target', type=int, help='Module target ID')
    parser_msf_module.add_argument('--creates-session', help='Name of MSF session to create')
    parser_msf_module.add_argument('--session', help='Name of existing MSF session ID/name to use')
    parser_msf_module.add_argument('--payload', help='Payload path (e.g., windows/...)')
    parser_msf_module.add_argument('--option', action='append', help='Module option key=value (repeatable)')
    parser_msf_module.add_argument('--payload-option', action='append', help='Payload option key=value (repeatable)')

    #  SetVar Command Arguments
    parser_setvar = command_subparsers.add_parser('setvar', help='Set a variable', parents=[common_args_parser])
    parser_setvar.add_argument('variable_name', help='Name of the variable to set')
    parser_setvar.add_argument('value_string', help='Value to assign to the variable')
    parser_setvar.add_argument('--encoder', help='Encoder to use (e.g., base64-encoder)')

    #  Debug Command Arguments
    parser_debug = command_subparsers.add_parser('debug', help='Debug output or pause', parents=[common_args_parser])
    parser_debug.add_argument('--message', help='Message to print (uses cmd field)')
    parser_debug.add_argument('--varstore', action=argparse.BooleanOptionalAction, help='Dump variable store')
    parser_debug.add_argument('--exit', action=argparse.BooleanOptionalAction, help='Exit after debugging')
    parser_debug.add_argument('--wait-for-key', action=argparse.BooleanOptionalAction, help='Wait for Enter key press')

    #  MsfSession Command Arguments
    parser_msf_session = command_subparsers.add_parser('msf-session', help='Interact with MSF session', parents=[common_args_parser])
    parser_msf_session.add_argument('session_name', help='Name/ID of the MSF session')
    parser_msf_session.add_argument('cmd_string', help='Command string to execute/write')
    parser_msf_session.add_argument('--stdapi', action=argparse.BooleanOptionalAction, help='Load stdapi')
    parser_msf_session.add_argument('--write', action=argparse.BooleanOptionalAction, help='Write raw data')
    parser_msf_session.add_argument('--read', action=argparse.BooleanOptionalAction, help='Read raw data')
    parser_msf_session.add_argument('--end-str', help='End string for run_with_output')

    #  SSH Command Arguments
    parser_ssh = command_subparsers.add_parser('ssh', help='Execute SSH command', parents=[common_args_parser])
    parser_ssh.add_argument('cmd_string', help='Command to execute via SSH')
    parser_ssh.add_argument('--hostname', help='Target hostname or IP')
    parser_ssh.add_argument('--port', type=int, help='SSH port')
    parser_ssh.add_argument('--username', help='SSH username')
    parser_ssh.add_argument('--password', help='SSH password')
    parser_ssh.add_argument('--passphrase', help='Passphrase for private key')
    parser_ssh.add_argument('--key-filename', help='Path to private key file')
    parser_ssh.add_argument('--creates-session', help='Name for the created SSH session')
    parser_ssh.add_argument('--session', help='Name of existing SSH session to use')
    parser_ssh.add_argument('--clear-cache', action=argparse.BooleanOptionalAction, help='Clear cached SSH connection settings')
    parser_ssh.add_argument('--timeout', type=float, help='Connection timeout in seconds')
    parser_ssh.add_argument('--jmp-hostname', help='Jumphost hostname')
    parser_ssh.add_argument('--jmp-port', type=int, help='Jumphost port')
    parser_ssh.add_argument('--jmp-username', help='Jumphost username')
    parser_ssh.add_argument('--interactive', action=argparse.BooleanOptionalAction, help='Use interactive shell')
    parser_ssh.add_argument('--command-timeout', type=int, help='Timeout for interactive read')
    parser_ssh.add_argument('--prompts', action='append', help='Expected prompt strings (repeatable)')
    parser_ssh.add_argument('--bin', action=argparse.BooleanOptionalAction, help='Send command as hex')

    #  SFTP Command Arguments
    parser_sftp = command_subparsers.add_parser('sftp', help='Transfer files via SFTP', parents=[common_args_parser])
    parser_sftp.add_argument('sftp_action', choices=['get', 'put'], help='SFTP action (get or put)')
    parser_sftp.add_argument('local_path', help='Local file path')
    parser_sftp.add_argument('remote_path', help='Remote file path')
    parser_sftp.add_argument('--mode', help='File mode (octal string, e.g., 755)')
    # Add SSH connection args common with SSH parser
    parser_sftp.add_argument('--hostname', help='Target hostname or IP')
    parser_sftp.add_argument('--port', type=int, help='SSH port')
    parser_sftp.add_argument('--username', help='SSH username')
    parser_sftp.add_argument('--password', help='SSH password')
    parser_sftp.add_argument('--passphrase', help='Passphrase for private key')
    parser_sftp.add_argument('--key-filename', help='Path to private key file')
    parser_sftp.add_argument('--creates-session', help='Name for the created SSH session')
    parser_sftp.add_argument('--session', help='Name of existing SSH session to use')
    parser_sftp.add_argument('--clear-cache', action=argparse.BooleanOptionalAction, help='Clear cached SSH connection settings')
    parser_sftp.add_argument('--timeout', type=float, help='Connection timeout in seconds')
    parser_sftp.add_argument('--jmp-hostname', help='Jumphost hostname')
    parser_sftp.add_argument('--jmp-port', type=int, help='Jumphost port')
    parser_sftp.add_argument('--jmp-username', help='Jumphost username')

    #  MsfPayload Command Arguments
    parser_msf_payload = command_subparsers.add_parser('msf-payload', help='Generate MSF payload', parents=[common_args_parser])
    parser_msf_payload.add_argument('payload_path', help='Payload path (e.g., windows/...)')
    parser_msf_payload.add_argument('--format', help='Output format (e.g., raw, exe)')
    parser_msf_payload.add_argument('--badchars', help='Characters to avoid')
    parser_msf_payload.add_argument('--force-encode', action=argparse.BooleanOptionalAction, help='Force encoding')
    parser_msf_payload.add_argument('--encoder', help='Encoder to use')
    parser_msf_payload.add_argument('--template', help='Path to template executable')
    parser_msf_payload.add_argument('--platform', help='Platform (e.g., windows)')
    parser_msf_payload.add_argument('--keep-template-working', action=argparse.BooleanOptionalAction, help='Keep template working')
    parser_msf_payload.add_argument('--nopsled-size', type=int, help='Size of NOP sled')
    parser_msf_payload.add_argument('--iter', type=int, help='Encoding iterations')
    parser_msf_payload.add_argument('--payload-option', action='append', help='Payload option key=value (repeatable)')
    parser_msf_payload.add_argument('--local-path', help='Path to save the generated payload')

    #  Sleep Command Arguments
    parser_sleep = command_subparsers.add_parser('sleep', help='Pause execution', parents=[common_args_parser])
    parser_sleep.add_argument('--seconds', type=int, help='Seconds to sleep')
    parser_sleep.add_argument('--min-sec', type=int, help='Minimum seconds for random sleep')
    parser_sleep.add_argument('--random', action=argparse.BooleanOptionalAction, help='Sleep random duration between min_sec and seconds')

    #  Include Command Arguments
    parser_include = command_subparsers.add_parser('include', help='Include commands from another file', parents=[common_args_parser])
    parser_include.add_argument('include_file_path', help='Path to the YAML file to include')

    #  HttpClient Command Arguments
    parser_http_client = command_subparsers.add_parser('http-client', help='Make HTTP requests', parents=[common_args_parser])
    parser_http_client.add_argument('method', choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'], help='HTTP method')
    parser_http_client.add_argument('url', help='Target URL')
    parser_http_client.add_argument('--output-headers', action=argparse.BooleanOptionalAction, help='Include response headers in output')
    parser_http_client.add_argument('--header', action='append', help='Request header key:value (repeatable)')
    parser_http_client.add_argument('--cookie', action='append', help='Request cookie key=value (repeatable)')
    parser_http_client.add_argument('--data', action='append', help='Request form data key=value (repeatable)')
    parser_http_client.add_argument('--local-path', help='Path to file for request body (PUT/POST)')
    parser_http_client.add_argument('--useragent', help='User-Agent string')
    parser_http_client.add_argument('--follow', action=argparse.BooleanOptionalAction, help='Follow redirects')
    parser_http_client.add_argument('--verify', action=argparse.BooleanOptionalAction, help='Verify SSL certificate')
    parser_http_client.add_argument('--http2', action=argparse.BooleanOptionalAction, help='Use HTTP/2')

    #  WebServ Command Arguments
    parser_webserv = command_subparsers.add_parser('webserv', help='Serve a file via HTTP', parents=[common_args_parser])
    parser_webserv.add_argument('file_to_serve', help='Path to the local file to serve')
    parser_webserv.add_argument('--port', type=int, help='Port to listen on')
    parser_webserv.add_argument('--address', help='Address to bind to')

    #  Sliver Listener Command Arguments
    parser_sliver_listener = command_subparsers.add_parser('sliver-listener', help='Start Sliver HTTPS listener', parents=[common_args_parser])
    parser_sliver_listener.add_argument('--host', help='Host address to bind listener')
    parser_sliver_listener.add_argument('--port', type=int, help='Port for listener')
    parser_sliver_listener.add_argument('--domain', help='Domain name for listener/certs')
    parser_sliver_listener.add_argument('--website', help='Website to host')
    parser_sliver_listener.add_argument('--acme', action=argparse.BooleanOptionalAction, help='Use ACME for certs')
    parser_sliver_listener.add_argument('--persistent', action=argparse.BooleanOptionalAction, help='Make listener persistent')
    parser_sliver_listener.add_argument('--enforce-otp', action=argparse.BooleanOptionalAction, help='Enforce OTP')
    parser_sliver_listener.add_argument('--randomize-jarm', action=argparse.BooleanOptionalAction, help='Randomize JARM fingerprint')
    parser_sliver_listener.add_argument('--long-poll-timeout', type=int, help='Long poll timeout')
    parser_sliver_listener.add_argument('--long-poll-jitter', type=int, help='Long poll jitter')
    parser_sliver_listener.add_argument('--timeout', type=int, help='Listener timeout')

    #  Sliver Generate Command Arguments
    parser_sliver_generate = command_subparsers.add_parser('sliver-generate', help='Generate Sliver implant', parents=[common_args_parser])
    parser_sliver_generate.add_argument('implant_name', help='Name for the implant profile')
    parser_sliver_generate.add_argument('c2url', help='C2 URL (e.g., https://domain:port)')
    parser_sliver_generate.add_argument('--target', choices=['darwin/amd64', 'darwin/arm64', 'linux/386', 'linux/amd64', 'windows/386', 'windows/amd64'], help='Target OS/Arch')
    parser_sliver_generate.add_argument('--format', choices=['EXECUTABLE', 'SERVICE', 'SHARED_LIB', 'SHELLCODE'], help='Output format')
    parser_sliver_generate.add_argument('--filepath', help='Local path to save generated implant')
    parser_sliver_generate.add_argument('--is-beacon', action=argparse.BooleanOptionalAction, help='Generate a beacon implant')
    parser_sliver_generate.add_argument('--beacon-interval', type=int, help='Beacon interval in seconds')
    parser_sliver_generate.add_argument('--run-at-load', action=argparse.BooleanOptionalAction, help='Run implant at load')
    parser_sliver_generate.add_argument('--evasion', action=argparse.BooleanOptionalAction, help='Enable evasion techniques')

    #  Sliver Session Command Arguments
    parser_sliver_session = command_subparsers.add_parser('sliver-session', help='Interact with Sliver session/beacon', parents=[common_args_parser])
    parser_sliver_session.add_argument('session_name', help='Name/ID of the session or beacon')
    parser_sliver_session.add_argument('sliver_sub_cmd', help='Sub-command (cd, ls, ps, execute, upload, etc.)')
    parser_sliver_session.add_argument('--beacon', action=argparse.BooleanOptionalAction, help='Interact with beacon instead of session')
    # Add args for sub-command parameters (use optional args)
    parser_sliver_session.add_argument('--remote-path', help='Remote path (for cd, ls, rm, upload, download)')
    parser_sliver_session.add_argument('--local-path', help='Local path (for upload, download, process_dump)')
    parser_sliver_session.add_argument('--recurse', action=argparse.BooleanOptionalAction, help='Recursive (for download)')
    parser_sliver_session.add_argument('--recursive', action=argparse.BooleanOptionalAction, help='Recursive (for rm)') # Alias for rm
    parser_sliver_session.add_argument('--is-ioc', action=argparse.BooleanOptionalAction, help='Mark uploaded file as IOC')
    parser_sliver_session.add_argument('--tcp', action=argparse.BooleanOptionalAction, help='Include TCP (for netstat)')
    parser_sliver_session.add_argument('--udp', action=argparse.BooleanOptionalAction, help='Include UDP (for netstat)')
    parser_sliver_session.add_argument('--ipv4', action=argparse.BooleanOptionalAction, help='Include IPv4 (for netstat)')
    parser_sliver_session.add_argument('--ipv6', action=argparse.BooleanOptionalAction, help='Include IPv6 (for netstat)')
    parser_sliver_session.add_argument('--listening', action=argparse.BooleanOptionalAction, help='Show listening ports (for netstat)')
    parser_sliver_session.add_argument('--exe-path', help='Executable path (for execute)')
    parser_sliver_session.add_argument('--args', nargs='*', help='Arguments for executable (for execute)')
    parser_sliver_session.add_argument('--output', action=argparse.BooleanOptionalAction, default=True, help='Capture output (for execute)')
    parser_sliver_session.add_argument('--pid', type=int, help='Process ID (for process_dump, terminate)')
    parser_sliver_session.add_argument('--force', action=argparse.BooleanOptionalAction, help='Force action (for rm, terminate)')

    #  Father Command Arguments
    parser_father = command_subparsers.add_parser('father', help='Generate Father rootkit', parents=[common_args_parser])
    # cmd is implicitly 'generate'
    parser_father.add_argument('--gid', help='Magic GID')
    parser_father.add_argument('--srcport', help='Magic source port')
    parser_father.add_argument('--epochtime', help='Magic epoch time')
    parser_father.add_argument('--env-var', help='Magic environment variable')
    parser_father.add_argument('--file-prefix', help='Magic file prefix')
    parser_father.add_argument('--preload-file', help='Preload filename')
    parser_father.add_argument('--hiddenport', help='Hidden port (hex)')
    parser_father.add_argument('--shell-pass', help='Password for bind/reverse shell')
    parser_father.add_argument('--install-path', help='Installation path on target')
    parser_father.add_argument('--local-path', help='Local path to save generated .so')
    parser_father.add_argument('--arch', choices=['amd64'], help='Architecture (currently only amd64)')
    parser_father.add_argument('--build-command', help='Build command (e.g., make)')

    #  RegEx Command Arguments
    parser_regex = command_subparsers.add_parser('regex', help='Parse variables using RegEx', parents=[common_args_parser])
    parser_regex.add_argument('pattern', help='The regular expression pattern')
    parser_regex.add_argument('--mode', choices=['search', 'split', 'findall', 'sub'], help='RegEx mode')
    parser_regex.add_argument('--replace', help='Replacement string (for sub mode)')
    parser_regex.add_argument('--input-var', help='Input variable name (default: RESULT_STDOUT)')
    parser_regex.add_argument('--output-map', action='append', help='Output variable mapping key=$MATCH_N (repeatable)')

    #  Json Command Arguments
    parser_json = command_subparsers.add_parser('json', help='Load variables from JSON', parents=[common_args_parser])
    parser_json.add_argument('--local-path', help='Path to the JSON file')
    parser_json.add_argument('--cmd-var', help='Variable name containing JSON string')
    parser_json.add_argument('--log-varstore', action=argparse.BooleanOptionalAction, help='Log varstore contents during execution')
    # Note: cmd field is not directly used here, path/var is primary input

    #  Tempfile Command Arguments
    parser_tempfile = command_subparsers.add_parser('tempfile', help='Create temporary file/directory', parents=[common_args_parser])
    parser_tempfile.add_argument('variable_name', help='Variable name to store the path')
    parser_tempfile.add_argument('--make-dir', action='store_true', help='Create a directory instead of a file') # Translates to cmd='dir'

    #  Vnc Command Arguments
    parser_vnc = command_subparsers.add_parser('vnc', help='Interact via VNC', parents=[common_args_parser])
    parser_vnc.add_argument('vnc_action', choices=['key', 'type', 'move', 'capture', 'click', 'rightclick', 'expectscreen', 'close'], help='VNC action to perform')
    parser_vnc.add_argument('--hostname', help='VNC server hostname')
    parser_vnc.add_argument('--port', type=int, help='VNC server port (use instead of display)')
    parser_vnc.add_argument('--display', type=int, help='VNC display number (use instead of port)')
    parser_vnc.add_argument('--password', help='VNC password')
    parser_vnc.add_argument('--key', help='Key to press (for action=key)')
    parser_vnc.add_argument('--input-str', help='String to type (for action=type)')
    parser_vnc.add_argument('--filename', help='Filename (for action=capture/expectscreen)')
    parser_vnc.add_argument('--x', type=int, help='X coordinate (for action=move)')
    parser_vnc.add_argument('--y', type=int, help='Y coordinate (for action=move)')
    parser_vnc.add_argument('--creates-session', help='Name for the created VNC session')
    parser_vnc.add_argument('--session', help='Name of existing VNC session to use')
    parser_vnc.add_argument('--maxrms', type=float, help='Max RMS diff (for action=expectscreen)')
    parser_vnc.add_argument('--expect-timeout', type=int, help='Timeout for expectscreen')
    parser_vnc.add_argument('--connection-timeout', type=int, help='VNC connection timeout')


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
