from typing import List, Literal, Union, Optional, Dict
from pydantic import BaseModel

# https://stackoverflow.com/questions/71539448/using-different-pydantic-models-depending-on-the-value-of-fields


class BaseCommand(BaseModel):
    error_if: Optional[str] = None
    error_if_not: Optional[str] = None
    loop_if: Optional[str] = None
    loop_if_not: Optional[str] = None
    loop_count: int = 3


class ShellCommand(BaseCommand):
    type: Literal['shell']
    cmd: str


class MsfCommand(BaseCommand):
    type: Literal['msf']
    cmd: str

class CommandConfig(BaseModel):
    loop_sleep: int = 5

class Config(BaseModel):
    cmd_config: CommandConfig = CommandConfig(loop_sleep=5)
    vars: Optional[Dict[str, str]] = None
    commands: List[Union[ShellCommand, MsfCommand]]
