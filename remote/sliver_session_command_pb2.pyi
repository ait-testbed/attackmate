import base_command_pb2 as _base_command_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SliverSessionCDPayload(_message.Message):
    __slots__ = ("remote_path",)
    REMOTE_PATH_FIELD_NUMBER: _ClassVar[int]
    remote_path: str
    def __init__(self, remote_path: _Optional[str] = ...) -> None: ...

class SliverSessionMKDIRPayload(_message.Message):
    __slots__ = ("remote_path",)
    REMOTE_PATH_FIELD_NUMBER: _ClassVar[int]
    remote_path: str
    def __init__(self, remote_path: _Optional[str] = ...) -> None: ...

class SliverSessionLSPayload(_message.Message):
    __slots__ = ("remote_path",)
    REMOTE_PATH_FIELD_NUMBER: _ClassVar[int]
    remote_path: str
    def __init__(self, remote_path: _Optional[str] = ...) -> None: ...

class SliverSessionDownloadPayload(_message.Message):
    __slots__ = ("remote_path", "local_path", "recurse")
    REMOTE_PATH_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSE_FIELD_NUMBER: _ClassVar[int]
    remote_path: str
    local_path: str
    recurse: bool
    def __init__(self, remote_path: _Optional[str] = ..., local_path: _Optional[str] = ..., recurse: bool = ...) -> None: ...

class SliverSessionUploadPayload(_message.Message):
    __slots__ = ("remote_path", "local_path", "recurse", "is_ioc")
    REMOTE_PATH_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSE_FIELD_NUMBER: _ClassVar[int]
    IS_IOC_FIELD_NUMBER: _ClassVar[int]
    remote_path: str
    local_path: str
    recurse: bool
    is_ioc: bool
    def __init__(self, remote_path: _Optional[str] = ..., local_path: _Optional[str] = ..., recurse: bool = ..., is_ioc: bool = ...) -> None: ...

class SliverSessionNetstatPayload(_message.Message):
    __slots__ = ("tcp", "udp", "ipv4", "ipv6", "listening")
    TCP_FIELD_NUMBER: _ClassVar[int]
    UDP_FIELD_NUMBER: _ClassVar[int]
    IPV4_FIELD_NUMBER: _ClassVar[int]
    IPV6_FIELD_NUMBER: _ClassVar[int]
    LISTENING_FIELD_NUMBER: _ClassVar[int]
    tcp: bool
    udp: bool
    ipv4: bool
    ipv6: bool
    listening: bool
    def __init__(self, tcp: bool = ..., udp: bool = ..., ipv4: bool = ..., ipv6: bool = ..., listening: bool = ...) -> None: ...

class SliverSessionExecPayload(_message.Message):
    __slots__ = ("exe", "args", "output")
    EXE_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    exe: str
    args: _containers.RepeatedScalarFieldContainer[str]
    output: bool
    def __init__(self, exe: _Optional[str] = ..., args: _Optional[_Iterable[str]] = ..., output: bool = ...) -> None: ...

class SliverSessionProcdumpPayload(_message.Message):
    __slots__ = ("local_path", "pid")
    LOCAL_PATH_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    local_path: str
    pid: str
    def __init__(self, local_path: _Optional[str] = ..., pid: _Optional[str] = ...) -> None: ...

class SliverSessionRmPayload(_message.Message):
    __slots__ = ("remote_path", "recursive", "force")
    REMOTE_PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    remote_path: str
    recursive: bool
    force: bool
    def __init__(self, remote_path: _Optional[str] = ..., recursive: bool = ..., force: bool = ...) -> None: ...

class SliverSessionTerminatePayload(_message.Message):
    __slots__ = ("pid", "force")
    PID_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    pid: str
    force: bool
    def __init__(self, pid: _Optional[str] = ..., force: bool = ...) -> None: ...

class SliverSessionCommandProto(_message.Message):
    __slots__ = ("base", "session", "beacon", "cd_payload", "mkdir_payload", "ls_payload", "download_payload", "upload_payload", "netstat_payload", "exec_payload", "procdump_payload", "rm_payload", "terminate_payload", "ps_command", "pwd_command", "ifconfig_command")
    BASE_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    BEACON_FIELD_NUMBER: _ClassVar[int]
    CD_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    MKDIR_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    LS_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    NETSTAT_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    EXEC_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PROCDUMP_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    RM_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TERMINATE_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PS_COMMAND_FIELD_NUMBER: _ClassVar[int]
    PWD_COMMAND_FIELD_NUMBER: _ClassVar[int]
    IFCONFIG_COMMAND_FIELD_NUMBER: _ClassVar[int]
    base: _base_command_pb2.BaseCommandFields
    session: str
    beacon: bool
    cd_payload: SliverSessionCDPayload
    mkdir_payload: SliverSessionMKDIRPayload
    ls_payload: SliverSessionLSPayload
    download_payload: SliverSessionDownloadPayload
    upload_payload: SliverSessionUploadPayload
    netstat_payload: SliverSessionNetstatPayload
    exec_payload: SliverSessionExecPayload
    procdump_payload: SliverSessionProcdumpPayload
    rm_payload: SliverSessionRmPayload
    terminate_payload: SliverSessionTerminatePayload
    ps_command: bool
    pwd_command: bool
    ifconfig_command: bool
    def __init__(self, base: _Optional[_Union[_base_command_pb2.BaseCommandFields, _Mapping]] = ..., session: _Optional[str] = ..., beacon: bool = ..., cd_payload: _Optional[_Union[SliverSessionCDPayload, _Mapping]] = ..., mkdir_payload: _Optional[_Union[SliverSessionMKDIRPayload, _Mapping]] = ..., ls_payload: _Optional[_Union[SliverSessionLSPayload, _Mapping]] = ..., download_payload: _Optional[_Union[SliverSessionDownloadPayload, _Mapping]] = ..., upload_payload: _Optional[_Union[SliverSessionUploadPayload, _Mapping]] = ..., netstat_payload: _Optional[_Union[SliverSessionNetstatPayload, _Mapping]] = ..., exec_payload: _Optional[_Union[SliverSessionExecPayload, _Mapping]] = ..., procdump_payload: _Optional[_Union[SliverSessionProcdumpPayload, _Mapping]] = ..., rm_payload: _Optional[_Union[SliverSessionRmPayload, _Mapping]] = ..., terminate_payload: _Optional[_Union[SliverSessionTerminatePayload, _Mapping]] = ..., ps_command: bool = ..., pwd_command: bool = ..., ifconfig_command: bool = ...) -> None: ...
