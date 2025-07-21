from __future__ import annotations
from typing import List, Optional, Dict

from .base import StrInt
from pydantic import BaseModel
from .commands import Commands


class Playbook(BaseModel):
    vars: Optional[Dict[str, List[StrInt] | StrInt]] = None
    commands: Commands
