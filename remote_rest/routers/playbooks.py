import logging
import os

import yaml
from fastapi import APIRouter, Body, HTTPException
from pydantic import ValidationError

from attackmate.schemas.playbook import Playbook
from remote_rest.schemas import PlaybookFileRequest, PlaybookResponseModel
from remote_rest.utils import varstore_to_state_model
from src.attackmate.attackmate import AttackMate
from src.attackmate.playbook_parser import parse_playbook

from ..state import attackmate_config

router = APIRouter(prefix='/playbooks', tags=['Playbooks'])
logger = logging.getLogger(__name__)
ALLOWED_PLAYBOOK_DIR = '/usr/local/share/attackmate/remote_playbooks/'  # MUST EXIST and be configured securely


# Playbook Execution
@router.post('/execute/yaml', response_model=PlaybookResponseModel)
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


@router.post('/execute/file', response_model=PlaybookResponseModel)
async def execute_playbook_from_file(request_body: PlaybookFileRequest):
    """
    Executes a playbook located at a specific path *on the server*.
    Uses a transient AttackMate instance.
    """
    # TODO ensure this only executes playbooks in certain locations, not arbitrary code -> read up on path traversal
    logger.info(f"Received request to execute playbook from file: {request_body.file_path}")
    try:
        # base directory exists
        if not os.path.isdir(ALLOWED_PLAYBOOK_DIR):
            logger.error(
                f"Configuration error: ALLOWED_PLAYBOOK_DIR '{ALLOWED_PLAYBOOK_DIR}' does not exist.")
            raise HTTPException(
                status_code=500, detail='Server configuration error: Playbook directory not found.')

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
        raise HTTPException(
            status_code=400, detail=f"Invalid playbook content in file '{request_body.file_path}': {e}")
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
