from pydantic import BaseModel
from typing import Optional


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


class Config(BaseModel):
    sliver_config: SliverConfig = SliverConfig(config_file=None)
    msf_config: MsfConfig = MsfConfig(password=None)
    cmd_config: CommandConfig = CommandConfig(loop_sleep=5)
