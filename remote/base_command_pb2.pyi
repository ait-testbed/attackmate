from google.protobuf import struct_pb2 as _struct_pb2
import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("type", "cmd", "parameters", "only_if", "error_if", "error_if_not", "loop_if", "loop_if_not", "loop_count", "exit_on_error", "save", "background", "kill_on_exit", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ONLY_IF_FIELD_NUMBER: _ClassVar[int]
    ERROR_IF_FIELD_NUMBER: _ClassVar[int]
    ERROR_IF_NOT_FIELD_NUMBER: _ClassVar[int]
    LOOP_IF_FIELD_NUMBER: _ClassVar[int]
    LOOP_IF_NOT_FIELD_NUMBER: _ClassVar[int]
    LOOP_COUNT_FIELD_NUMBER: _ClassVar[int]
    EXIT_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    SAVE_FIELD_NUMBER: _ClassVar[int]
    BACKGROUND_FIELD_NUMBER: _ClassVar[int]
    KILL_ON_EXIT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    type: str
    cmd: str
    parameters: _struct_pb2.Struct
    only_if: str
    error_if: str
    error_if_not: str
    loop_if: str
    loop_if_not: str
    loop_count: str
    exit_on_error: bool
    save: str
    background: bool
    kill_on_exit: bool
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, type: _Optional[str] = ..., cmd: _Optional[str] = ..., parameters: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., only_if: _Optional[str] = ..., error_if: _Optional[str] = ..., error_if_not: _Optional[str] = ..., loop_if: _Optional[str] = ..., loop_if_not: _Optional[str] = ..., loop_count: _Optional[str] = ..., exit_on_error: bool = ..., save: _Optional[str] = ..., background: bool = ..., kill_on_exit: bool = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class BaseCommandFields(_message.Message):
    __slots__ = ("only_if", "error_if", "error_if_not", "loop_if", "loop_if_not", "loop_count", "exit_on_error", "save", "background", "kill_on_exit", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ONLY_IF_FIELD_NUMBER: _ClassVar[int]
    ERROR_IF_FIELD_NUMBER: _ClassVar[int]
    ERROR_IF_NOT_FIELD_NUMBER: _ClassVar[int]
    LOOP_IF_FIELD_NUMBER: _ClassVar[int]
    LOOP_IF_NOT_FIELD_NUMBER: _ClassVar[int]
    LOOP_COUNT_FIELD_NUMBER: _ClassVar[int]
    EXIT_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    SAVE_FIELD_NUMBER: _ClassVar[int]
    BACKGROUND_FIELD_NUMBER: _ClassVar[int]
    KILL_ON_EXIT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    only_if: str
    error_if: str
    error_if_not: str
    loop_if: str
    loop_if_not: str
    loop_count: str
    exit_on_error: bool
    save: str
    background: bool
    kill_on_exit: bool
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, only_if: _Optional[str] = ..., error_if: _Optional[str] = ..., error_if_not: _Optional[str] = ..., loop_if: _Optional[str] = ..., loop_if_not: _Optional[str] = ..., loop_count: _Optional[str] = ..., exit_on_error: bool = ..., save: _Optional[str] = ..., background: bool = ..., kill_on_exit: bool = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ExecuteCommandResponse(_message.Message):
    __slots__ = ("result", "updated_state")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_STATE_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.CommandResult
    updated_state: _common_pb2.VariableStoreState
    def __init__(self, result: _Optional[_Union[_common_pb2.CommandResult, _Mapping]] = ..., updated_state: _Optional[_Union[_common_pb2.VariableStoreState, _Mapping]] = ...) -> None: ...
