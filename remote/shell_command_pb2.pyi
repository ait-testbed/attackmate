import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShellCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "interactive", "creates_session", "session", "command_timeout", "command_shell", "bin", "read")
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    INTERACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATES_SESSION_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    COMMAND_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    COMMAND_SHELL_FIELD_NUMBER: _ClassVar[int]
    BIN_FIELD_NUMBER: _ClassVar[int]
    READ_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    interactive: bool
    creates_session: str
    session: str
    command_timeout: str
    command_shell: str
    bin: bool
    read: bool
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., interactive: bool = ..., creates_session: _Optional[str] = ..., session: _Optional[str] = ..., command_timeout: _Optional[str] = ..., command_shell: _Optional[str] = ..., bin: bool = ..., read: bool = ...) -> None: ...
