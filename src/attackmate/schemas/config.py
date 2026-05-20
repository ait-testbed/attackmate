from pydantic import BaseModel
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
    sliver_config: SliverConfig = SliverConfig(config_file=None)
    msf_config: MsfConfig = MsfConfig(password=None)
    cmd_config: CommandConfig = CommandConfig(loop_sleep=5, command_delay=0)
    bettercap_config: Dict[str, BettercapConfig] = {}
    remote_config: Dict[str, RemoteConfig] = {}
