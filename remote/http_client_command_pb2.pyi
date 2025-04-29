import base_command_pb2 as _base_command_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpClientCommandProto(_message.Message):
    __slots__ = ("base", "cmd", "url", "output_headers", "headers", "cookies", "data", "local_path", "useragent", "follow", "verify", "http2")
    class HeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class CookiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    BASE_FIELD_NUMBER: _ClassVar[int]
    CMD_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_HEADERS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    COOKIES_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    USERAGENT_FIELD_NUMBER: _ClassVar[int]
    FOLLOW_FIELD_NUMBER: _ClassVar[int]
    VERIFY_FIELD_NUMBER: _ClassVar[int]
    HTTP2_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    cmd: str
    url: str
    output_headers: bool
    headers: _containers.ScalarMap[str, str]
    cookies: _containers.ScalarMap[str, str]
    data: _containers.ScalarMap[str, str]
    local_path: str
    useragent: str
    follow: bool
    verify: bool
    http2: bool
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., cmd: _Optional[str] = ..., url: _Optional[str] = ..., output_headers: bool = ..., headers: _Optional[_Mapping[str, str]] = ..., cookies: _Optional[_Mapping[str, str]] = ..., data: _Optional[_Mapping[str, str]] = ..., local_path: _Optional[str] = ..., useragent: _Optional[str] = ..., follow: bool = ..., verify: bool = ..., http2: bool = ...) -> None: ...
