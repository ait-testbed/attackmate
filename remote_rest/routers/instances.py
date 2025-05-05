import logging
import uuid
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Path

from remote_rest.schemas import (InstanceCreationResponse,
                                 VariableStoreStateModel)
from remote_rest.utils import varstore_to_state_model
from src.attackmate.attackmate import AttackMate
from src.attackmate.schemas.config import Config

from ..state import (get_attackmate_config, get_instance_by_id,
                     get_instances_dict, get_persistent_instance)

router = APIRouter(tags=['Instances'])
logger = logging.getLogger(__name__)


# THIS CAN POTENTIALLY BE USED TO GNERATE NEW INSTANCES WITH IDS
# @router.post('', response_model=InstanceCreationResponse)
# async def create_new_instance(
#     instances: Dict[str, AttackMate] = Depends(get_instances_dict),
#     config: Config = Depends(get_attackmate_config)
# ):
#     """Creates a new persistent AttackMate instance and returns its ID."""
#     instance_id = str(uuid.uuid4())
#     logger.info(f"Creating instance ID: {instance_id}")
#     try:
#         instance = AttackMate(playbook=None, config=config, varstore=None)
#         instances[instance_id] = instance  # Modify injected dict
#         logger.info(f"Instance {instance_id} created.")
#         return InstanceCreationResponse(instance_id=instance_id, message='Instance created.')
#     except Exception as e:
#         logger.error(f"Failed to create instance {instance_id}: {e}", exc_info=True)
#         if instance_id in instances:
#             del instances[instance_id]
#             raise HTTPException(status_code=500, detail='Failed to create instance.')


# @router.delete('/{instance_id}', status_code=204)
# async def delete_instance_route(
#     instance_id: str = Path(...),
#     instances: Dict[str, AttackMate] = Depends(get_instances_dict)
# ):
#     instance = instances.pop(instance_id, None)
#     if not instance:
#         raise HTTPException(status_code=404, detail=f"Instance '{instance_id}' not found.")
#     logger.info(f"Deleting instance {instance_id}...")
#     try:
#         instance.clean_session_stores()
#         instance.pm.kill_or_wait_processes()
#     except Exception as e:
#         logger.error(f"Error during cleanup: {e}", exc_info=True)


@router.get('/{instance_id}/state', response_model=VariableStoreStateModel)
async def get_instance_state(instance: AttackMate = Depends(get_instance_by_id)):
    return varstore_to_state_model(instance.varstore)


@router.get('/state', response_model=VariableStoreStateModel)
async def get_persistent_instance_state(instance: AttackMate = Depends(get_persistent_instance)):
    return varstore_to_state_model(instance.varstore)
