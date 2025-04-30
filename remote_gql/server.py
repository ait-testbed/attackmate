import uvicorn
import logging
import sys
from typing import Optional, Union
from strawberry.asgi import GraphQL
from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.responses import Response

from .schema import schema
from src.attackmate.attackmate import AttackMate
from src.attackmate.playbook_parser import parse_config
from src.attackmate.logging_setup import initialize_logger, initialize_output_logger, initialize_json_logger
from src.attackmate.schemas.config import Config


attackmate_instance: Optional[AttackMate] = None
attackmate_config: Optional[Config] = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


class AttackMateGraphQL(GraphQL):
    async def get_context(
        self, request: Union[Request, WebSocket], response: Optional[Union[Response, WebSocket]] = None
    ):
        # This provides the context for each request
        # access the global instances here
        if not attackmate_instance or not attackmate_config:
            logger.error('AttackMate instance or config not initialized before context creation!')
            # exception handling
            return None
        return {
            'request': request,
            'response': response,
            'attackmate_instance': attackmate_instance,
            'attackmate_config': attackmate_config,
        }


def create_app():
    global attackmate_instance, attackmate_config

    # Loggers
    initialize_logger(debug=True, append_logs=False)
    initialize_output_logger(debug=True, append_logs=False)
    initialize_json_logger(json=True, append_logs=False)
    logger.info('AttackMate loggers initialized.')

    # Config
    attackmate_config = parse_config(config_file=None, logger=logger)
    logger.info('AttackMate configuration loaded.')

    #  persistent AttackMate Instance
    logger.info('Creating persistent AttackMate instance...')
    # Pass empty initial playbook/vars
    attackmate_instance = AttackMate(playbook=None, config=attackmate_config, varstore=None)
    logger.info('Persistent AttackMate instance created.')

    graphql_app = AttackMateGraphQL(schema, graphql_ide=True)

    return graphql_app


def shutdown():
    logger.warning('Server shutting down...')
    if attackmate_instance:
        logger.info('Cleaning up AttackMate instance...')
        try:
            attackmate_instance.clean_session_stores()
            logger.info('AttackMate cleaup finished.')
        except Exception as e:
            logger.error(f"Error during AttackMate cleanup: {e}", exc_info=True)
    sys.exit(0)


if __name__ == '__main__':

    app = create_app()
    logger.info('Starting Uvicorn server...')
    try:
        uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info', log_config=None)
        # Disabled default logging to have attackmate.log, attackmate.json etc. but maybe uvicorn logging needed

    finally:
        logger.info('Uvicorn server stopped. Performing application cleanup.')
        shutdown()
