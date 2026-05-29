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
        # Old configs had a single flat MsfConfig dict (keys: password, ssl, port, server, uri).
        # New configs are Dict[str, MsfConfig] with named connections.
        # Detect the old format by checking for known MsfConfig field names at the top level.
        # .intersection() only requires one match, unspecified fields fall back to their Pydantic defaults.
        # Wrapping it under 'default'
        # !! Note !! : connection names that coincide with MsfConfig field names (e.g. 'server')
        # would be misdetected as old format and should be avoided.
        if isinstance(v, dict) and {'password', 'ssl', 'port', 'server', 'uri'}.intersection(v.keys()):
            return {'default': v}
        return v

    @field_validator('sliver_config', mode='before')
    @classmethod
    def migrate_sliver_config(cls, v):
        # Same backwards-compatibility migration as migrate_msf_config above.
        if isinstance(v, dict) and {'config_file'}.intersection(v.keys()):
            return {'default': v}
        return v
