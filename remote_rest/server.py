import uvicorn
import logging
import uuid
import yaml
import os
from fastapi import FastAPI, HTTPException, Body, Path, Request
from fastapi.responses import JSONResponse
from pydantic import Field, ValidationError, BaseModel
from typing import Dict, Any, Optional

from attackmate.schemas.base import BaseCommand
from src.attackmate.attackmate import AttackMate
from src.attackmate.playbook_parser import parse_config, parse_playbook
from src.attackmate.logging_setup import initialize_logger, initialize_output_logger, initialize_json_logger
from src.attackmate.schemas.config import Config
from src.attackmate.schemas.playbook import Playbook
from src.attackmate.variablestore import VariableStore
from src.attackmate.result import Result as AttackMateResult
from src.attackmate.execexception import ExecException


from src.attackmate.schemas.shell import ShellCommand
from src.attackmate.schemas.sleep import SleepCommand
from src.attackmate.schemas.debug import DebugCommand
from src.attackmate.schemas.setvar import SetVarCommand
from src.attackmate.schemas.tempfile import TempfileCommand
# ADD IMPORTS FOR OTHER COMMAND PYDANTIC SCHEMAS HERE


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


class InstanceCreationResponse(BaseModel):
    instance_id: str
    message: str


class PlaybookFileRequest(BaseModel):
    file_path: str = Field(..., description='Path to the playbook file RELATIVE to a predefined server directory.')


# Logging
initialize_logger(debug=True, append_logs=False)
initialize_output_logger(debug=True, append_logs=False)
initialize_json_logger(json=True, append_logs=False)
logger = logging.getLogger('attackmate_api')  # specific logger for the API
# TODO make this configurable via request, even also per attackmate instance?
logger.setLevel(logging.DEBUG)


# This holds persistent AttackMate instances
INSTANCES: Dict[str, AttackMate] = {}

# load config
# TODO pass/modify configs in the request
try:
    attackmate_config: Config = parse_config(config_file=None, logger=logger)
    logger.info('Global AttackMate configuration loaded.')
except Exception as e:
    logger.error(f"Failed to load AttackMate config on startup: {e}", exc_info=True)
    exit(1)


# HElpers

def get_attackmate_instance(instance_id: str) -> AttackMate:
    """Retrieves an instance"""
    instance = INSTANCES.get(instance_id)
    if not instance:
        logger.warning(f"AttackMate instance '{instance_id}' not found.")
        raise HTTPException(status_code=404, detail=f"AttackMate instance '{instance_id}' not found.")
    return instance


def create_persistent_instance() -> str:
    """Creates a new persistent AttackMate instance and returns its ID."""
    instance_id = str(uuid.uuid4())
    logger.info(f"Creating new persistent AttackMate instance with ID: {instance_id}")
    try:
        # Create with empty playbook/vars
        instance = AttackMate(playbook=None, config=attackmate_config, varstore=None)
        INSTANCES[instance_id] = instance
        logger.info(f"Instance {instance_id} created successfully.")
        return instance_id
    except Exception as e:
        logger.error(f"Failed to create persistent instance {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail='Failed to create AttackMate instance.')


def varstore_to_state_model(varstore: VariableStore) -> VariableStoreStateModel:
    """Converts AttackMate VariableStore to Pydantic VariableStoreStateModel."""
    combined_vars: Dict[str, Any] = {}
    combined_vars.update(varstore.variables)
    combined_vars.update(varstore.lists)
    return VariableStoreStateModel(variables=combined_vars)


async def run_command_on_instance(instance: AttackMate, command_data: BaseCommand) -> AttackMateResult:
    """Runs a command on a given AttackMate instance."""
    try:
        logger.info(f"Executing command type '{command_data.type}' on instance") # type: ignore
        # TODO does this work? need to pass command class object here?
        result = instance.run_command(command_data)
        logger.info(f"Command execution finished. RC: {result.returncode}")
        return result
    except (ExecException, SystemExit) as e:
        logger.error(f"AttackMate execution error: {e}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during instance.run_command: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during command execution: {e}")


app = FastAPI(
    title='AttackMate REST API',
    description='API for remote control of AttackMate instances and playbook execution.',
    version='1.0.0'
)


# Error handling
# --- Error Handling ---
@app.exception_handler(ExecException)
async def attackmate_execution_exception_handler(request: Request, exc: ExecException):
    logger.error(f"AttackMate Execution Exception: {exc}")
    return JSONResponse(
        status_code=400, # bad request?
        content={
            'detail': 'AttackMate command execution failed',
            'error_message': str(exc),
            'instance_id': None
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, SystemExit):
        logger.error(f"Command triggered SystemExit with code {exc.code}")
        return JSONResponse(
            status_code=400,  # client-side error pattern
            content={
                'detail': 'Command execution led to termination request',
                'error_message': f"SystemExit triggered (likely due to error condition like 'exit_on_error' or 'error_if'). Exit code: {exc.code}",
                'instance_id': None
            },
        )
    # Re-raise other exceptions for specific hanfling?
    raise exc


# Endpoints

# Playbook Execution
@app.post('/playbooks/execute/yaml', response_model=PlaybookResponseModel, tags=['Playbooks'])
async def execute_playbook_from_yaml(playbook_yaml: str = Body(..., media_type='application/yaml')):
    """
    Executes a playbook provided as YAML content in the request body.
    Use a transient AttackMate instance.
    """
    logger.info('Received request to execute playbook from YAML content.')
    am_instance = None
    try:
        playbook_dict = yaml.safe_load(playbook_yaml)
        if not playbook_dict:
            raise ValueError('Received empty or invalid playbook YAML content.')
        playbook = Playbook.model_validate(playbook_dict)

        logger.info('Creating transient AttackMate instance...')
        am_instance = AttackMate(playbook=playbook, config=attackmate_config, varstore=None)
        return_code = am_instance.main()
        final_state = varstore_to_state_model(am_instance.varstore)
        logger.info(f"Transient playbook execution finished. return code {return_code}")
        return PlaybookResponseModel(
            success=(return_code == 0),
            message='Playbook execution finished.',
            final_state=final_state
        )
    except (yaml.YAMLError, ValidationError, ValueError) as e:
        logger.error(f"Playbook validation/parsing error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid playbook YAML: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during playbook execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error during playbook execution: {e}")
    finally:
        if am_instance:
            logger.info('Cleaning up transient playbook instance.')
            try:
                am_instance.clean_session_stores()
                am_instance.pm.kill_or_wait_processes()
            except Exception as cleanup_e:
                logger.error(f"Error cleaning transient instance: {cleanup_e}", exc_info=True)


@app.post('/playbooks/execute/file', response_model=PlaybookResponseModel, tags=['Playbooks'])
async def execute_playbook_from_file(request_body: PlaybookFileRequest):
    """
    Executes a playbook located at a specific path *on the server*.
    Uses a transient AttackMate instance.
    """
    # TODO ensure this only executes playbooks in certain locations, not arbitrary code -> read up on path traversal
    logger.info(f"Received request to execute playbook from file: {request_body.file_path}")

    # Define a secure base directory where playbooks are allowed
    ALLOWED_PLAYBOOK_DIR = '/usr/local/share/attackmate/remote_playbooks/'  # MUST EXIST and be configured securely
    try:
        # base directory exists
        if not os.path.isdir(ALLOWED_PLAYBOOK_DIR):
            logger.error(f"Configuration error: ALLOWED_PLAYBOOK_DIR '{ALLOWED_PLAYBOOK_DIR}' does not exist.")
            raise HTTPException(status_code=500, detail='Server configuration error: Playbook directory not found.')

        requested_path = os.path.normpath(request_body.file_path)
        # Disallow absolute paths or paths trying to go up directories
        if os.path.isabs(requested_path) or requested_path.startswith('..'):
            raise ValueError('Invalid playbook path specified.')

        full_path = os.path.join(ALLOWED_PLAYBOOK_DIR, requested_path)
        # Final check: ensure the resolved path is still within the allowed directory
        if not os.path.abspath(full_path).startswith(os.path.abspath(ALLOWED_PLAYBOOK_DIR)):
            raise ValueError('Invalid playbook path specified (path traversal attempt ).')

        # Check if the file exists
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"Playbook file not found atpath: {full_path}")

    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Invalid or non-existent playbook path requested: {request_body.file_path} -> {e}")
        raise HTTPException(status_code=400, detail=f"Invalid or non-existent playbook file path: {e}")
    except Exception as e:
        logger.error(f"Error processing playbook path: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail='Server error processing file path.')

    am_instance = None
    try:
        # Parse the playbook file
        logger.info(f"Parsing playbook from: {full_path}")
        playbook = parse_playbook(full_path, logger)

        logger.info('Creating transient AttackMate instance')
        am_instance = AttackMate(playbook=playbook, config=attackmate_config, varstore=None)
        return_code = am_instance.main()
        final_state = varstore_to_state_model(am_instance.varstore)
        logger.info(f"Transient playbook execution finished. RC: {return_code}")
        return PlaybookResponseModel(
            success=(return_code == 0),
            message=f"Playbook '{request_body.file_path}' execution finished.",
            final_state=final_state
        )
    except (ValidationError, ValueError) as e:
        logger.error(f"Playbook validation error from file '{full_path}': {e}")
        raise HTTPException(status_code=400, detail=f"Invalid playbook content in file '{request_body.file_path}': {e}")
    except Exception as e:
        logger.error(f"Unexpected error during playbook file execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error during playbook execution: {e}")
    finally:
        if am_instance:
            logger.info('Cleaning up transient playbook instance.')
            try:
                am_instance.clean_session_stores()
                am_instance.pm.kill_or_wait_processes()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")


# Attackmate Instances

@app.post('/instances', response_model=InstanceCreationResponse, tags=['Instances'])
async def create_new_instance():
    """Creates a new persistent AttackMate instance and returns its ID."""
    instance_id = create_persistent_instance()
    return InstanceCreationResponse(instance_id=instance_id, message='AttackMate instance created successfully.')


@app.delete('/instances/{instance_id}', status_code=204, tags=['Instances'])
async def delete_instance(instance_id: str = Path(..., description='ID of the instance to delete.')):
    """Deletes a persistent AttackMate instance."""
    instance = INSTANCES.pop(instance_id, None)
    if not instance:
        raise HTTPException(status_code=404, detail=f"Instance '{instance_id}' not found.")
    logger.info(f"Deleting instance {instance_id}...")
    try:
        instance.clean_session_stores()
        instance.pm.kill_or_wait_processes()
        logger.info(f"Instance {instance_id} cleaned up and deleted.")
    except Exception as e:
        logger.error(f"Error during cleanup while deleting instance {instance_id}: {e}", exc_info=True)
    return


@app.get('/instances/{instance_id}/state', response_model=VariableStoreStateModel, tags=['Instances'])
async def get_instance_state(instance_id: str = Path(..., description='ID of the instance.')):
    """Gets the current variable store state for an instance."""
    instance = get_attackmate_instance(instance_id)
    return varstore_to_state_model(instance.varstore)


# Command Endpoints
@app.post('/instances/{instance_id}/shell', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_shell_command(
    command: ShellCommand,
    instance_id: str = Path(..., description='ID of the target instance.'),
):
    """Executes a shell command on the specified AttackMate instance."""
    logger.info(f"Received shell command request for instance {instance_id}.")
    instance = get_attackmate_instance(instance_id)  # Raise 404 if not found
    attackmate_result = await run_command_on_instance(instance, command)  # WHat about backgorund commands

    # response
    result_model = CommandResultModel(
        success=(attackmate_result.returncode == 0 if attackmate_result.returncode is not None else True),  # Success if RC 0 or None (background)
        stdout=attackmate_result.stdout,
        returncode=attackmate_result.returncode
    )
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@app.post('/instances/{instance_id}/sleep', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_sleep_command(
    command: SleepCommand,
    instance_id: str = Path(..., description='ID of the target instance.'),
):
    """Executes a sleep command on the specified AttackMate instance."""
    logger.info(f"Received sleep command request for instance {instance_id}.")
    instance = get_attackmate_instance(instance_id)
    attackmate_result = await run_command_on_instance(instance, command)
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@app.post('/instances/{instance_id}/debug', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_debug_command(
    command: DebugCommand,
    instance_id: str = Path(..., description='ID of the target instance.'),
):
    """Executes a debug command on the specified AttackMate instance."""
    logger.info(f"Received debug command request for instance {instance_id}.")
    instance = get_attackmate_instance(instance_id)
    attackmate_result = await run_command_on_instance(instance, command)
    # Debug command might trigger SystemExit if command.exit is True
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@app.post('/instances/{instance_id}/setvar', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_setvar_command(
    command: SetVarCommand,
    instance_id: str = Path(..., description='ID of the target instance.'),
):
    """Executes a setvar command on the specified AttackMate instance."""
    logger.info(f"Received setvar command request for instance {instance_id}.")
    instance = get_attackmate_instance(instance_id)
    attackmate_result = await run_command_on_instance(instance, command)
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@app.post('/instances/{instance_id}/mktemp', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_mktemp_command(
    command: TempfileCommand,
    instance_id: str = Path(..., description='ID of the target instance.'),
):
    """Executes an mktemp command (create temp file/dir) on the specified instance."""
    logger.info(f"Received mktemp command request for instance {instance_id}.")
    instance = get_attackmate_instance(instance_id)
    attackmate_result = await run_command_on_instance(instance, command)
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)

#  Add other command endpoints here

if __name__ == '__main__':
    logger.info('Starting AttackMate FastAPI server')

    # `uvicorn remote_rest.server:app --reload` for development
    uvicorn.run(app, host='0.0.0.0', port=8000, log_config=None)  # Disable default logging to enable attackmate internal logging? how to have both

    # TODO sort out logs for different instances
    # TODO return logs to caller
    # TODO limit max. concurent instance number
    # TODO concurrency for several instances?
    # TODO add authentication
    # TODO queue requests for instances
    # TODO dynamic configuration of attackmate config
    # TODO make logging (debug, json etc) configurable at runtime (endpoint or user query paramaters?)
    # TODO ALLOWED_PLAYBOOK_DIR -> define in and load from configs
    # TODO add swagger examples
    # TODO generate OpenAPI schema
    # TODO seperate router modules?
