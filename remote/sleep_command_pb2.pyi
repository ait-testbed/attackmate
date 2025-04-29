import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SleepCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "min_sec", "seconds", "random")
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    MIN_SEC_FIELD_NUMBER: _ClassVar[int]
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    RANDOM_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    min_sec: str
    seconds: str
    random: bool
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., min_sec: _Optional[str] = ..., seconds: _Optional[str] = ..., random: bool = ...) -> None: ...
