import logging
from typing import Dict
from pymetasploit3.msfrpc import MsfRpcClient, MsfAuthError
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.config import MsfConfig
from attackmate.execexception import ExecException


class MsfClientMixin:
    msf_config: Dict[str, MsfConfig]
    _msf_clients: Dict[str, MsfRpcClient]
    logger: logging.Logger

    def _resolve_connection(self, command: BaseCommand) -> str:
        conn = getattr(command, 'connection', None)
        if conn:
            return conn
        if self.msf_config:
            conn_name = next(iter(self.msf_config))
            self.logger.debug(f'No connection specified, using default: {conn_name}')
            return conn_name
        raise ExecException('No MSF connections configured')

    def _get_client(self, conn_name: str) -> MsfRpcClient:
        if conn_name not in self._msf_clients:
            if conn_name not in self.msf_config:
                raise ExecException(f"MSF connection '{conn_name}' not found in config")
            config = self.msf_config[conn_name]
            self.logger.debug(
                f"Connecting to MSF server '{conn_name}' at {config.server}:{config.port} (ssl={config.ssl})"
            )
            try:
                self._msf_clients[conn_name] = MsfRpcClient(**config.model_dump())
            except IOError as e:
                self.logger.error(e)
                raise ExecException(f'MSF connection failed: {e}')
            except MsfAuthError as e:
                self.logger.error(e)
                raise ExecException(f'MSF authentication failed: {e}')
        return self._msf_clients[conn_name]
