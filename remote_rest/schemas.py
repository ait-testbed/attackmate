from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class VariableStoreStateModel(BaseModel):
    variables: Dict[str, Any] = {}


class CommandResultModel(BaseModel):
    success: bool
    stdout: Optional[str] = None
    returncode: Optional[int] = None
    error_message: Optional[str] = None


class ExecutionResponseModel(BaseModel):
    result: CommandResultModel
    state: VariableStoreStateModel
    instance_id: Optional[str] = None


class PlaybookResponseModel(BaseModel):
    success: bool
    message: str
    final_state: Optional[VariableStoreStateModel] = None
    instance_id: Optional[str] = None


class InstanceCreationResponse(BaseModel):
    instance_id: str
    message: str


class PlaybookFileRequest(BaseModel):
    file_path: str = Field(...,
                           description='Path to the playbook file RELATIVE to a predefined server directory.')
    debug: bool = Field(
        False,
        description='If true, the playbook will be executed in debug mode. '
    )
