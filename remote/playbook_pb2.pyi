import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecutePlaybookRequest(_message.Message):
    __slots__ = ("playbook_yaml", "initial_state")
    PLAYBOOK_YAML_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_FIELD_NUMBER: _ClassVar[int]
    playbook_yaml: str
    initial_state: _common_pb2.VariableStoreState
    def __init__(self, playbook_yaml: _Optional[str] = ..., initial_state: _Optional[_Union[_common_pb2.VariableStoreState, _Mapping]] = ...) -> None: ...

class ExecutePlaybookResponse(_message.Message):
    __slots__ = ("success", "message", "final_state")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FINAL_STATE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    final_state: _common_pb2.VariableStoreState
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., final_state: _Optional[_Union[_common_pb2.VariableStoreState, _Mapping]] = ...) -> None: ...
