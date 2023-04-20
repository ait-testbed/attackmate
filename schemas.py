from typing import List, Literal, Union
from pydantic import BaseModel

# https://stackoverflow.com/questions/71539448/using-different-pydantic-models-depending-on-the-value-of-fields

class ShellCommand(BaseModel):
    type: Literal['shell']
    cmd: str

class MsfCommand(BaseModel):
    type: Literal['msf']
    cmd: str


class Config(BaseModel):
    commands: List[Union[ShellCommand,MsfCommand]]

