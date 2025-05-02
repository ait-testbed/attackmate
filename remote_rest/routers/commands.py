import logging

from fastapi import APIRouter, Depends, HTTPException, Path

from attackmate.attackmate import AttackMate
from attackmate.schemas.base import BaseCommand
from remote_rest.schemas import CommandResultModel, ExecutionResponseModel
from remote_rest.utils import varstore_to_state_model
from src.attackmate.execexception import ExecException
from src.attackmate.result import Result as AttackMateResult
from src.attackmate.schemas.debug import DebugCommand
from src.attackmate.schemas.setvar import SetVarCommand
from src.attackmate.schemas.shell import ShellCommand
from src.attackmate.schemas.sleep import SleepCommand
from src.attackmate.schemas.tempfile import TempfileCommand

from ..state import get_instance_by_id

# ADD IMPORTS FOR OTHER COMMAND PYDANTIC SCHEMAS HERE


router = APIRouter(prefix='/instances/{instance_id}', tags=['Commands'])
logger = logging.getLogger(__name__)


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


# Command Endpoints
@router.post('/shell', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_shell_command(
    command: ShellCommand,
    instance_id: str = Path(...),
    instance: AttackMate = Depends(get_instance_by_id)
):
    """Executes a shell command on the specified AttackMate instance."""
    attackmate_result = await run_command_on_instance(instance, command)  # WHat about backgorund commands

    # response
    result_model = CommandResultModel(
        success=(attackmate_result.returncode == 0 if attackmate_result.returncode is not None else True),  # Success if RC 0 or None (background)
        stdout=attackmate_result.stdout,
        returncode=attackmate_result.returncode
    )
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@router.post('/sleep', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_sleep_command(
    command: SleepCommand,
    instance_id: str = Path(...),
    instance: AttackMate = Depends(get_instance_by_id)
):
    """Executes a sleep command on the specified AttackMate instance."""
    attackmate_result = await run_command_on_instance(instance, command)
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@router.post('/debug', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_debug_command(
    command: DebugCommand,
    instance_id: str = Path(...),
    instance: AttackMate = Depends(get_instance_by_id)
):
    """Executes a debug command on the specified AttackMate instance."""
    attackmate_result = await run_command_on_instance(instance, command)
    # Debug command might trigger SystemExit if command.exit is True
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@router.post('/setvar', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_setvar_command(
    command: SetVarCommand,
    instance_id: str = Path(...),
    instance: AttackMate = Depends(get_instance_by_id)
):
    """Executes a setvar command on the specified AttackMate instance."""
    attackmate_result = await run_command_on_instance(instance, command)
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)


@router.post('/mktemp', response_model=ExecutionResponseModel, tags=['Commands'])
async def execute_mktemp_command(
    command: TempfileCommand,
    instance_id: str = Path(...),
    instance: AttackMate = Depends(get_instance_by_id)
):
    """Executes an mktemp command (create temp file/dir) on the specified instance."""
    attackmate_result = await run_command_on_instance(instance, command)
    result_model = CommandResultModel(success=True, stdout=attackmate_result.stdout, returncode=attackmate_result.returncode)
    state_model = varstore_to_state_model(instance.varstore)
    return ExecutionResponseModel(result=result_model, state=state_model, instance_id=instance_id)

#  Add other command endpoints here
