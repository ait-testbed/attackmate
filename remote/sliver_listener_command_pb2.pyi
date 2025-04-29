import base_command_pb2 as _base_command_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SliverListenerCommandProto(_message.Message):
    __slots__ = ("base", "host", "port", "domain", "website", "acme", "persistent", "enforce_otp", "randomize_jarm", "long_poll_timeout", "long_poll_jitter", "timeout")
    BASE_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    ACME_FIELD_NUMBER: _ClassVar[int]
    PERSISTENT_FIELD_NUMBER: _ClassVar[int]
    ENFORCE_OTP_FIELD_NUMBER: _ClassVar[int]
    RANDOMIZE_JARM_FIELD_NUMBER: _ClassVar[int]
    LONG_POLL_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    LONG_POLL_JITTER_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    host: str
    port: str
    domain: str
    website: str
    acme: bool
    persistent: bool
    enforce_otp: bool
    randomize_jarm: bool
    long_poll_timeout: str
    long_poll_jitter: str
    timeout: str
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., host: _Optional[str] = ..., port: _Optional[str] = ..., domain: _Optional[str] = ..., website: _Optional[str] = ..., acme: bool = ..., persistent: bool = ..., enforce_otp: bool = ..., randomize_jarm: bool = ..., long_poll_timeout: _Optional[str] = ..., long_poll_jitter: _Optional[str] = ..., timeout: _Optional[str] = ...) -> None: ...
