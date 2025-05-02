import uvicorn
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from attackmate.execexception import ExecException

from src.attackmate.playbook_parser import parse_config

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.attackmate.logging_setup import (initialize_json_logger,
                                          initialize_logger,
                                          initialize_output_logger)


from remote_rest.routers import commands, instances, playbooks
import remote_rest.state as state

# Logging
initialize_logger(debug=True, append_logs=False)
initialize_output_logger(debug=True, append_logs=False)
initialize_json_logger(json=True, append_logs=False)
logger = logging.getLogger('attackmate_api')  # specific logger for the API
# TODO make this configurable via request, even also per attackmate instance?
logger.setLevel(logging.DEBUG)


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
            raise RuntimeError('Failed to load essential AttackMate configuration (parse_config returned None).')
        # Initialize the INSTANCES dict (it's already defined globally in state.py)
        state.INSTANCES.clear()
        logger.info('Instances dictionary initialized.')
        #  any other async startup tasks ?

    except Exception as e:
        logger.critical(f"Failed to initialize during startup lifespan: {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize application state: {e}") from e

    yield  # Application runs here

    # Code to run when the application is shutting down
    logger.warning('AttackMate API shutting down (lifespan)... Cleaning up instances...')
    instance_ids = list(state.INSTANCES.keys())
    for instance_id in instance_ids:
        instance = state.INSTANCES.pop(instance_id, None)
        if instance:
            logger.info(f"Cleaning up instance {instance_id}...")
            try:
                # blocking?
                instance.clean_session_stores()
                instance.pm.kill_or_wait_processes()
            except Exception as e:
                logger.error(f"Error cleaning up instance {instance_id}: {e}", exc_info=True)
    logger.info('Instance cleanup complete (lifespan).')


app = FastAPI(
    title='AttackMate API',
    description='API for remote control of AttackMate instances and playbook execution.',
    version='1.0.0',
    lifespan=lifespan)

# Include Routers
app.include_router(instances.router, prefix='/instances')
app.include_router(playbooks.router)
app.include_router(commands.router)


# Exception Handling
@app.exception_handler(ExecException)
async def attackmate_execution_exception_handler(request: Request, exc: ExecException):
    logger.error(f"AttackMate Execution Exception: {exc}")
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

if __name__ == '__main__':
    uvicorn.run('remote_rest.main:app', host='0.0.0.0', port=8000, reload=True, log_config=None,)
