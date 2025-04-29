import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VncCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "hostname", "port", "display", "password", "key", "input", "filename", "x", "y", "creates_session", "session", "maxrms", "expect_timeout", "connection_timeout")
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    CREATES_SESSION_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    MAXRMS_FIELD_NUMBER: _ClassVar[int]
    EXPECT_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    hostname: str
    port: str
    display: str
    password: str
    key: str
    input: str
    filename: str
    x: int
    y: int
    creates_session: str
    session: str
    maxrms: float
    expect_timeout: int
    connection_timeout: int
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., hostname: _Optional[str] = ..., port: _Optional[str] = ..., display: _Optional[str] = ..., password: _Optional[str] = ..., key: _Optional[str] = ..., input: _Optional[str] = ..., filename: _Optional[str] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., creates_session: _Optional[str] = ..., session: _Optional[str] = ..., maxrms: _Optional[float] = ..., expect_timeout: _Optional[int] = ..., connection_timeout: _Optional[int] = ...) -> None: ...
