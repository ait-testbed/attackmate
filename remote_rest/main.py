from contextlib import asynccontextmanager
import sys
from typing import AsyncGenerator
import os
import uvicorn
from attackmate.execexception import ExecException
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from src.attackmate.attackmate import AttackMate
from src.attackmate.logging_setup import (initialize_json_logger,
                                          initialize_logger,
                                          initialize_output_logger,
                                          initialize_api_logger)
from src.attackmate.playbook_parser import parse_config

import remote_rest.state as state
from remote_rest.routers import commands, instances, playbooks

from .auth_utils import create_access_token, get_user_hash, verify_password
from .schemas import TokenResponse

CERT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(CERT_DIR, 'key.pem')
CERT_FILE = os.path.join(CERT_DIR, 'cert.pem')

# Logging
initialize_logger(debug=True, append_logs=False)
initialize_output_logger(debug=True, append_logs=False)
initialize_json_logger(json=True, append_logs=False)
logger = initialize_api_logger(debug=True, append_logs=False)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    #  Code to run before the application starts accepting requests
    logger.info('AttackMate API starting up (lifespan)...')
    try:
        # Load global config on startup and assign to the variable in state.py
        loaded_config = parse_config(config_file=None, logger=logger)
        if loaded_config:
            state.attackmate_config = loaded_config
            logger.info('Global AttackMate configuration loaded.')
        else:
            raise RuntimeError(
                'Failed to load essential AttackMate configuration (parse_config returned None).')
        # Initialize the INSTANCES dict (it's already defined globally in state.py)
        state.INSTANCES.clear()
        # instantiate the Instance in the INSTANCES dict
        state.INSTANCES['default_context'] = AttackMate(playbook=None, config=loaded_config, varstore=None)
        logger.info('Instances dictionary initialized.')
        #  any other async startup tasks ?

    except Exception as e:
        logger.critical(f'Failed to initialize during startup lifespan: {e}', exc_info=True)
        raise RuntimeError(f'Failed to initialize application state: {e}') from e

    yield  # Application runs here

    # Code to run when the application is shutting down
    logger.warning('AttackMate API shutting down (lifespan)... Cleaning up instances...')
    instance_ids = list(state.INSTANCES.keys())
    for instance_id in instance_ids:
        instance = state.INSTANCES.pop(instance_id, None)
        if instance:
            logger.info(f'Cleaning up instance {instance_id}...')
            try:
                # blocking?
                instance.clean_session_stores()
                instance.pm.kill_or_wait_processes()
            except Exception as e:
                logger.error(f'Error cleaning up instance {instance_id}: {e}', exc_info=True)
    logger.info('Instance cleanup complete (lifespan).')


app = FastAPI(
    title='AttackMate API',
    description='API for remote control of AttackMate instances and playbook execution.',
    version='1.0.0',
    lifespan=lifespan)


# Exception Handling
@app.exception_handler(ExecException)
async def attackmate_execution_exception_handler(request: Request, exc: ExecException):
    logger.error(f'AttackMate Execution Exception: {exc}')
    return JSONResponse(
        status_code=400,
        content={
            'detail': 'AttackMate command execution failed',
            'error_message': str(exc),
            'instance_id': None
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, SystemExit):
        logger.error(f'Command triggered SystemExit with code {exc.code}')
        return JSONResponse(
            status_code=400,  # client-side error pattern
            content={
                'detail': 'Command execution led to termination request',
                'error_message': (
                    f"SystemExit triggered (likely due to error condition like 'exit_on_error'). "
                    f'Exit code: {exc.code}'
                ),
                'instance_id': None
            },
        )
    # Re-raise other exceptions for specific hanfling?
    raise exc


# Login endpoint
@app.post('/login', response_model=TokenResponse, tags=['Auth'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticates user and returns an access token."""
    logger.info(f'Login attempt for user: {form_data.username}')
    hashed_password = get_user_hash(form_data.username)
    if not hashed_password:
        logger.warning(f"Login failed: User '{form_data.username}' not found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if not verify_password(form_data.password, hashed_password):
        logger.warning(f"Login failed: Invalid password for user '{form_data.username}'.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # vlid password ->  create token
    access_token = create_access_token(username=form_data.username)
    logger.info(f"Login successful for user '{form_data.username}'. Token created.")
    # Return token
    return TokenResponse(access_token=access_token, token_type='bearer')

# Include Routers
app.include_router(instances.router, prefix='/instances')
app.include_router(playbooks.router)
app.include_router(commands.router)


# Root Endpoint
@app.get('/', include_in_schema=False)
async def root():
    return {'message': 'AttackMate API is running. Use /login to authenticate. See /docs.'}

if __name__ == '__main__':
    if not os.path.exists(KEY_FILE):
        logger.critical(f'SSL Error: Key file not found at {KEY_FILE}')
        sys.exit(1)
    if not os.path.exists(CERT_FILE):
        logger.critical(f'SSL Error: Certificate file not found at {CERT_FILE}')
        sys.exit(1)
    uvicorn.run('remote_rest.main:app',
                host='0.0.0.0',
                port=8443,
                reload=False,

                ssl_keyfile=KEY_FILE,
                ssl_certfile=CERT_FILE)
