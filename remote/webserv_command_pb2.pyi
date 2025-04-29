import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WebServCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "local_path", "port", "address")
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    local_path: str
    port: str
    address: str
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., local_path: _Optional[str] = ..., port: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...
