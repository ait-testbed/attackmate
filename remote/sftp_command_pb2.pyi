import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SFTPCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "hostname", "port", "username", "password", "passphrase", "key_filename", "creates_session", "session", "clear_cache", "timeout", "jmp_hostname", "jmp_port", "jmp_username", "remote_path", "local_path", "mode")
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PASSPHRASE_FIELD_NUMBER: _ClassVar[int]
    KEY_FILENAME_FIELD_NUMBER: _ClassVar[int]
    CREATES_SESSION_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    CLEAR_CACHE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    JMP_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    JMP_PORT_FIELD_NUMBER: _ClassVar[int]
    JMP_USERNAME_FIELD_NUMBER: _ClassVar[int]
    REMOTE_PATH_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    hostname: str
    port: str
    username: str
    password: str
    passphrase: str
    key_filename: str
    creates_session: str
    session: str
    clear_cache: bool
    timeout: float
    jmp_hostname: str
    jmp_port: str
    jmp_username: str
    remote_path: str
    local_path: str
    mode: str
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., hostname: _Optional[str] = ..., port: _Optional[str] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., passphrase: _Optional[str] = ..., key_filename: _Optional[str] = ..., creates_session: _Optional[str] = ..., session: _Optional[str] = ..., clear_cache: bool = ..., timeout: _Optional[float] = ..., jmp_hostname: _Optional[str] = ..., jmp_port: _Optional[str] = ..., jmp_username: _Optional[str] = ..., remote_path: _Optional[str] = ..., local_path: _Optional[str] = ..., mode: _Optional[str] = ...) -> None: ...
