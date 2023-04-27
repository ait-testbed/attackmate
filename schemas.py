from typing import List, Literal, Union, Optional, Dict
from pydantic import BaseModel

# https://stackoverflow.com/questions/71539448/using-different-pydantic-models-depending-on-the-value-of-fields


class BaseCommand(BaseModel):
    error_if: Optional[str] = None


class ShellCommand(BaseCommand):
    type: Literal['shell']
    cmd: str


class MsfCommand(BaseCommand):
    type: Literal['msf']
    cmd: str


class Config(BaseModel):
    vars: Optional[Dict[str, str]] = None
    commands: List[Union[ShellCommand, MsfCommand]]
