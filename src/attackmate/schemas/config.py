from pydantic import BaseModel, field_validator
from typing import Optional, Dict


class SliverConfig(BaseModel):
    config_file: Optional[str] = None


class MsfConfig(BaseModel):
    password: Optional[str] = None
    ssl: bool = True
    port: int = 55553
    server: Optional[str] = '127.0.0.1'
    uri: Optional[str] = '/api/'


class CommandConfig(BaseModel):
    loop_sleep: int = 5
    command_delay: float = 0
    command_delay_jitter: bool = False
    command_delay_jitter_min: float = 0.5
    command_delay_jitter_max: float = 2.0


class BettercapConfig(BaseModel):
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    cafile: Optional[str] = None


class RemoteConfig(BaseModel):
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    cafile: Optional[str] = None


class Config(BaseModel):
    sliver_config: Dict[str, SliverConfig] = {}
    msf_config: Dict[str, MsfConfig] = {}
    cmd_config: CommandConfig = CommandConfig(loop_sleep=5, command_delay=0)
    bettercap_config: Dict[str, BettercapConfig] = {}
    remote_config: Dict[str, RemoteConfig] = {}

    @field_validator('msf_config', mode='before')
    @classmethod
    def migrate_msf_config(cls, v):
        # Handle a bare MsfConfig instance passed by embedded-API callers.
        if isinstance(v, MsfConfig):
            return {'default': v}
        # Old configs had a single flat MsfConfig dict (keys: password, ssl, port, server, uri)
        # Detect the old format by  a known field name AND at least one scalar value
        # avoids misdetecting a new-format connection named e.g. 'server'.
        # wrapping in "default"
        msf_fields = {'password', 'ssl', 'port', 'server', 'uri'}
        if (isinstance(v, dict)
                and msf_fields.intersection(v.keys())
                and any(not isinstance(val, dict) for val in v.values())):
            return {'default': v}
        return v

    @field_validator('sliver_config', mode='before')
    @classmethod
    def migrate_sliver_config(cls, v):
        # Handle a bare SliverConfig instance passed by embedded-API callers.
        if isinstance(v, SliverConfig):
            return {'default': v}
        # Same check as above (only one field: config_file)
        if (isinstance(v, dict)
                and {'config_file'}.intersection(v.keys())
                and any(not isinstance(val, dict) for val in v.values())):
            return {'default': v}
        return v
