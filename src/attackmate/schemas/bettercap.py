from attackmate.command import CommandRegistry
from attackmate.schemas.base import BaseCommand
from typing import Literal, Optional, Dict, Any
from pydantic import model_validator


class BettercapCommand(BaseCommand):
    cmd: Literal['get_events',
                 'get_session_modules',
                 'get_session_env',
                 'get_session_gateway',
                 'get_session_hid',
                 'get_session_ble',
                 'get_session_interface',
                 'get_session_options',
                 'get_session_lan',
                 'get_session_packets',
                 'get_session_started_at',
                 'get_session_wifi',
                 'delete_api_events',
                 'get_file',
                 'post_api_session']
    type: Literal['bettercap']
    connection: Optional[str] = None
    mac: Optional[str] = None
    filename: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @model_validator(mode='after')
    def check_cmd_requirements(cls, values):
        cmd = values.cmd

        if values.background:
            raise ValueError('background mode is unsupported for VNC')
        if cmd == 'post_api_session' and values.data is None:
            raise ValueError('post_api_session requires the parameter data')
        if cmd == 'get_file' and values.filename is None:
            raise ValueError('get_file requires the parameter filename')

        return values



"""
  Please note that get_file() needs a parameter and
  therefor it is not a BettercapGetCommand!
"""


# @CommandRegistry.register('bettercap', 'get_file')
# class BettercapGetFileCommand(BaseCommand):
#     cmd: Literal['get_file']
#     type: Literal['bettercap']
#     filename: str
#     connection: Optional[str] = None
# 
# 
# @CommandRegistry.register('bettercap', 'post_api_session')
# class BettercapPostApiSessionCommand(BaseCommand):
#     cmd: Literal['post_api_session']
#     type: Literal['bettercap']
#     data: Optional[Dict[str, Any]] = None
#     connection: Optional[str] = None

