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
    current_token: Optional[str] = Field(None, description='Renewed auth token for subsequent requests.')


class PlaybookResponseModel(BaseModel):
    success: bool
    message: str
    final_state: Optional[VariableStoreStateModel] = None
    instance_id: Optional[str] = None
    attackmate_log: Optional[str] = Field(None, description='Content of the attackmate.log for this run.')
    output_log: Optional[str] = Field(None, description='Content of the output.log for this run.')
    current_token: Optional[str] = Field(None, description='Renewed auth token for subsequent requests.')


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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
