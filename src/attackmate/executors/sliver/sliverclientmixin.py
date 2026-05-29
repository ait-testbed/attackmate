import logging
from typing import Dict
from sliver import SliverClientConfig, SliverClient
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.config import SliverConfig
from attackmate.execexception import ExecException


class SliverClientMixin:
    sliver_config: Dict[str, SliverConfig]
    _sliver_clients: Dict[str, SliverClient]
    logger: logging.Logger

    def _resolve_connection(self, command: BaseCommand) -> str:
        conn = getattr(command, 'connection', None)
        if conn:
            return conn
        if self.sliver_config:
            conn_name = next(iter(self.sliver_config))
            self.logger.debug(f'No connection specified, using default: {conn_name}')
            return conn_name
        raise ExecException('No Sliver connections configured')

    def _get_client(self, conn_name: str) -> SliverClient:
        if conn_name not in self._sliver_clients:
            if conn_name not in self.sliver_config:
                raise ExecException(f"Sliver connection '{conn_name}' not found in config")
            config = self.sliver_config[conn_name]
            if not config.config_file:
                raise ExecException(f"Sliver connection '{conn_name}' has no config_file")
            client_config = SliverClientConfig.parse_config_file(config.config_file)
            self._sliver_clients[conn_name] = SliverClient(client_config)
        return self._sliver_clients[conn_name]
