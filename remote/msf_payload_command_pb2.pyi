import base_command_pb2 as _base_command_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsfPayloadCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "format", "badchars", "force_encode", "encoder", "template", "platform", "keep_template_working", "nopsled_size", "iter", "payload_options", "local_path")
    class PayloadOptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    BADCHARS_FIELD_NUMBER: _ClassVar[int]
    FORCE_ENCODE_FIELD_NUMBER: _ClassVar[int]
    ENCODER_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    KEEP_TEMPLATE_WORKING_FIELD_NUMBER: _ClassVar[int]
    NOPSLED_SIZE_FIELD_NUMBER: _ClassVar[int]
    ITER_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    format: str
    badchars: str
    force_encode: bool
    encoder: str
    template: str
    platform: str
    keep_template_working: bool
    nopsled_size: str
    iter: str
    payload_options: _containers.ScalarMap[str, str]
    local_path: str
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., format: _Optional[str] = ..., badchars: _Optional[str] = ..., force_encode: bool = ..., encoder: _Optional[str] = ..., template: _Optional[str] = ..., platform: _Optional[str] = ..., keep_template_working: bool = ..., nopsled_size: _Optional[str] = ..., iter: _Optional[str] = ..., payload_options: _Optional[_Mapping[str, str]] = ..., local_path: _Optional[str] = ...) -> None: ...
