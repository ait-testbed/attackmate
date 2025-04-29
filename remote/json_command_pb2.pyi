import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JsonCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "local_path", "varstore")
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    VARSTORE_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    local_path: str
    varstore: bool
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., local_path: _Optional[str] = ..., varstore: bool = ...) -> None: ...
