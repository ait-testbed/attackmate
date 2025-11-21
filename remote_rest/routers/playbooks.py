import logging
import os
import uuid
from typing import Optional

import yaml
from attackmate.schemas.playbook import Playbook
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query
from pydantic import ValidationError
from src.attackmate.attackmate import AttackMate
from src.attackmate.playbook_parser import parse_playbook

from remote_rest.auth_utils import API_KEY_HEADER_NAME, get_current_user
from remote_rest.schemas import PlaybookFileRequest, PlaybookResponseModel
from remote_rest.utils import varstore_to_state_model

from ..log_utils import instance_logging
from ..state import attackmate_config

router = APIRouter(prefix='/playbooks', tags=['Playbooks'])
logger = logging.getLogger(__name__)

# helper t0 read logfile
def read_log_file(log_path: Optional[str]) -> Optional[str]:
    if not log_path or not os.path.exists(log_path):
        return None
    try:
        with open(log_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read log file '{log_path}': {e}")
        return f"Error reading log file: {e}"

# Playbook Execution


@router.post('/execute/yaml', response_model=PlaybookResponseModel)
async def execute_playbook_from_yaml(playbook_yaml: str = Body(..., media_type='application/yaml'),
                                     debug: bool = Query(
                                         False,
                                         description="Enable debug logging for this request's instance log."
),
                                     current_user: str = Depends(get_current_user),
                                     x_auth_token: Optional[str] = Header(None, alias=API_KEY_HEADER_NAME)):
    """
    Executes a playbook provided as YAML content in the request body.
    Use a transient AttackMate instance.
    """
    logger.info('Received request to execute playbook from YAML content.')
    instance_id = str(uuid.uuid4())
    log_level = logging.DEBUG if debug else logging.INFO
    with instance_logging(instance_id, log_level) as log_files:
        attackmate_log_path, output_log_path, json_log_path = log_files
        try:
            playbook_dict = yaml.safe_load(playbook_yaml)
            if not playbook_dict:
                raise ValueError('Received empty or invalid playbook YAML content.')
            playbook = Playbook.model_validate(playbook_dict)
            logger.info(f"Creating transient AttackMate instance, ID: {instance_id}")
            am_instance = AttackMate(playbook=playbook, config=attackmate_config, varstore=None)
            return_code = am_instance.main()
            final_state = varstore_to_state_model(am_instance.varstore)
            logger.info(f"Transient playbook execution finished. return code {return_code}")
            attackmate_log = read_log_file(attackmate_log_path)
            output_log = read_log_file(output_log_path)
            json_log = read_log_file(json_log_path)
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

    return PlaybookResponseModel(
        success=(return_code == 0),
        message='Playbook execution finished.',
        final_state=final_state,
        instance_id=instance_id,
        attackmate_log=attackmate_log,
        output_log=output_log,
        json_log=json_log,
        current_token=x_auth_token
    )


