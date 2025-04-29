import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SliverGenerateCommandProto(_message.Message):
    __slots__ = ("base", "target", "c2url", "format", "name", "filepath", "IsBeacon", "BeaconInterval", "RunAtLoad", "Evasion")
    BASE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    C2URL_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    ISBEACON_FIELD_NUMBER: _ClassVar[int]
    BEACONINTERVAL_FIELD_NUMBER: _ClassVar[int]
    RUNATLOAD_FIELD_NUMBER: _ClassVar[int]
    EVASION_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    target: str
    c2url: str
    format: str
    name: str
    filepath: str
    IsBeacon: bool
    BeaconInterval: str
    RunAtLoad: bool
    Evasion: bool
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., target: _Optional[str] = ..., c2url: _Optional[str] = ..., format: _Optional[str] = ..., name: _Optional[str] = ..., filepath: _Optional[str] = ..., IsBeacon: bool = ..., BeaconInterval: _Optional[str] = ..., RunAtLoad: bool = ..., Evasion: bool = ...) -> None: ...
