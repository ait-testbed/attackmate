from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandResult(_message.Message):
    __slots__ = ("success", "stdout", "returncode", "error_message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    RETURNCODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    stdout: str
    returncode: int
    error_message: str
    def __init__(self, success: bool = ..., stdout: _Optional[str] = ..., returncode: _Optional[int] = ..., error_message: _Optional[str] = ...) -> None: ...

class VariableValue(_message.Message):
    __slots__ = ("null_value", "number_value", "string_value", "bool_value", "struct_value", "list_value")
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRUCT_VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_VALUE_FIELD_NUMBER: _ClassVar[int]
    null_value: _struct_pb2.NullValue
    number_value: float
    string_value: str
    bool_value: bool
    struct_value: _struct_pb2.Struct
    list_value: _struct_pb2.ListValue
    def __init__(self, null_value: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., number_value: _Optional[float] = ..., string_value: _Optional[str] = ..., bool_value: bool = ..., struct_value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., list_value: _Optional[_Union[_struct_pb2.ListValue, _Mapping]] = ...) -> None: ...

class VariableStoreState(_message.Message):
    __slots__ = ("variables",)
    class VariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: VariableValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[VariableValue, _Mapping]] = ...) -> None: ...
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    variables: _containers.MessageMap[str, VariableValue]
    def __init__(self, variables: _Optional[_Mapping[str, VariableValue]] = ...) -> None: ...
