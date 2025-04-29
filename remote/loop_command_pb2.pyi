from . import base_command_pb2 as _base_command_pb2
from . import msf_module_command_pb2 as _msf_module_command_pb2
from . import msf_session_command_pb2 as _msf_session_command_pb2
from . import msf_payload_command_pb2 as _msf_payload_command_pb2
from . import shell_command_pb2 as _shell_command_pb2
from . import sleep_command_pb2 as _sleep_command_pb2
from . import ssh_command_pb2 as _ssh_command_pb2
from . import sftp_command_pb2 as _sftp_command_pb2
from . import debug_command_pb2 as _debug_command_pb2
from . import setvar_command_pb2 as _setvar_command_pb2
from . import regex_command_pb2 as _regex_command_pb2
from . import tempfile_command_pb2 as _tempfile_command_pb2
from . import include_command_pb2 as _include_command_pb2
from . import webserv_command_pb2 as _webserv_command_pb2
from . import http_client_command_pb2 as _http_client_command_pb2
from . import json_command_pb2 as _json_command_pb2
from . import sliver_listener_command_pb2 as _sliver_listener_command_pb2
from . import sliver_generate_command_pb2 as _sliver_generate_command_pb2
from . import sliver_session_command_pb2 as _sliver_session_command_pb2
from . import vnc_command_pb2 as _vnc_command_pb2
from . import father_command_pb2 as _father_command_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnyNestedCommand(_message.Message):
    __slots__ = ("shell_command", "msf_module_command", "msf_session_command", "msf_payload_command", "sleep_command", "ssh_command", "sftp_command", "debug_command", "setvar_command", "regex_command", "tempfile_command", "include_command", "webserv_command", "http_client_command", "json_command", "sliver_listener_command", "sliver_generate_command", "sliver_session_command", "vnc_command", "father_command")
    SHELL_COMMAND_FIELD_NUMBER: _ClassVar[int]
    MSF_MODULE_COMMAND_FIELD_NUMBER: _ClassVar[int]
    MSF_SESSION_COMMAND_FIELD_NUMBER: _ClassVar[int]
    MSF_PAYLOAD_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SLEEP_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SSH_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SFTP_COMMAND_FIELD_NUMBER: _ClassVar[int]
    DEBUG_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SETVAR_COMMAND_FIELD_NUMBER: _ClassVar[int]
    REGEX_COMMAND_FIELD_NUMBER: _ClassVar[int]
    TEMPFILE_COMMAND_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_COMMAND_FIELD_NUMBER: _ClassVar[int]
    WEBSERV_COMMAND_FIELD_NUMBER: _ClassVar[int]
    HTTP_CLIENT_COMMAND_FIELD_NUMBER: _ClassVar[int]
    JSON_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SLIVER_LISTENER_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SLIVER_GENERATE_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SLIVER_SESSION_COMMAND_FIELD_NUMBER: _ClassVar[int]
    VNC_COMMAND_FIELD_NUMBER: _ClassVar[int]
    FATHER_COMMAND_FIELD_NUMBER: _ClassVar[int]
    shell_command: _shell_command_pb2.ShellCommandProto
    msf_module_command: _msf_module_command_pb2.MsfModuleCommandProto
    msf_session_command: _msf_session_command_pb2.MsfSessionCommandProto
    msf_payload_command: _msf_payload_command_pb2.MsfPayloadCommandProto
    sleep_command: _sleep_command_pb2.SleepCommandProto
    ssh_command: _ssh_command_pb2.SSHCommandProto
    sftp_command: _sftp_command_pb2.SFTPCommandProto
    debug_command: _debug_command_pb2.DebugCommandProto
    setvar_command: _setvar_command_pb2.SetVarCommandProto
    regex_command: _regex_command_pb2.RegExCommandProto
    tempfile_command: _tempfile_command_pb2.TempfileCommandProto
    include_command: _include_command_pb2.IncludeCommandProto
    webserv_command: _webserv_command_pb2.WebServCommandProto
    http_client_command: _http_client_command_pb2.HttpClientCommandProto
    json_command: _json_command_pb2.JsonCommandProto
    sliver_listener_command: _sliver_listener_command_pb2.SliverListenerCommandProto
    sliver_generate_command: _sliver_generate_command_pb2.SliverGenerateCommandProto
    sliver_session_command: _sliver_session_command_pb2.SliverSessionCommandProto
    vnc_command: _vnc_command_pb2.VncCommandProto
    father_command: _father_command_pb2.FatherCommandProto
    def __init__(self, shell_command: _Optional[_Union[_shell_command_pb2.ShellCommandProto, _Mapping]] = ..., msf_module_command: _Optional[_Union[_msf_module_command_pb2.MsfModuleCommandProto, _Mapping]] = ..., msf_session_command: _Optional[_Union[_msf_session_command_pb2.MsfSessionCommandProto, _Mapping]] = ..., msf_payload_command: _Optional[_Union[_msf_payload_command_pb2.MsfPayloadCommandProto, _Mapping]] = ..., sleep_command: _Optional[_Union[_sleep_command_pb2.SleepCommandProto, _Mapping]] = ..., ssh_command: _Optional[_Union[_ssh_command_pb2.SSHCommandProto, _Mapping]] = ..., sftp_command: _Optional[_Union[_sftp_command_pb2.SFTPCommandProto, _Mapping]] = ..., debug_command: _Optional[_Union[_debug_command_pb2.DebugCommandProto, _Mapping]] = ..., setvar_command: _Optional[_Union[_setvar_command_pb2.SetVarCommandProto, _Mapping]] = ..., regex_command: _Optional[_Union[_regex_command_pb2.RegExCommandProto, _Mapping]] = ..., tempfile_command: _Optional[_Union[_tempfile_command_pb2.TempfileCommandProto, _Mapping]] = ..., include_command: _Optional[_Union[_include_command_pb2.IncludeCommandProto, _Mapping]] = ..., webserv_command: _Optional[_Union[_webserv_command_pb2.WebServCommandProto, _Mapping]] = ..., http_client_command: _Optional[_Union[_http_client_command_pb2.HttpClientCommandProto, _Mapping]] = ..., json_command: _Optional[_Union[_json_command_pb2.JsonCommandProto, _Mapping]] = ..., sliver_listener_command: _Optional[_Union[_sliver_listener_command_pb2.SliverListenerCommandProto, _Mapping]] = ..., sliver_generate_command: _Optional[_Union[_sliver_generate_command_pb2.SliverGenerateCommandProto, _Mapping]] = ..., sliver_session_command: _Optional[_Union[_sliver_session_command_pb2.SliverSessionCommandProto, _Mapping]] = ..., vnc_command: _Optional[_Union[_vnc_command_pb2.VncCommandProto, _Mapping]] = ..., father_command: _Optional[_Union[_father_command_pb2.FatherCommandProto, _Mapping]] = ...) -> None: ...

class LoopCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "commands", "break_if")
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    BREAK_IF_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    commands: _containers.RepeatedCompositeFieldContainer[AnyNestedCommand]
    break_if: str
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., commands: _Optional[_Iterable[_Union[AnyNestedCommand, _Mapping]]] = ..., break_if: _Optional[str] = ...) -> None: ...
