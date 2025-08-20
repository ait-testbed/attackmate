from attackmate.command import CommandRegistry
from attackmate.schemas.base import BaseCommand
from typing import Literal, Optional, Dict, Any

"""
  BettercapGetCommand includes all API-GetCommands
  that can be executed without any parameter.
  for example: get_events()
"""


class BettercapGetCommand(BaseCommand):
    type: Literal['bettercap']
    connection: Optional[str] = None


@CommandRegistry.register('bettercap', 'get_events')
class BettercapGetEventsCommand(BettercapGetCommand):
    cmd: Literal['get_events']


@CommandRegistry.register('bettercap', 'get_session_modules')
class BettercapGetSessionModulesCommand(BettercapGetCommand):
    cmd: Literal['get_session_modules']


@CommandRegistry.register('bettercap', 'get_session_env')
class BettercapGetSessionEnvCommand(BettercapGetCommand):
    cmd: Literal['get_session_env']


@CommandRegistry.register('bettercap', 'get_session_gateway')
class BettercapGetSessionGatewayCommand(BettercapGetCommand):
    cmd: Literal['get_session_gateway']


@CommandRegistry.register('bettercap', 'get_session_hid')
class BettercapGetSessionHidCommand(BettercapGetCommand):
    cmd: Literal['get_session_hid']


@CommandRegistry.register('bettercap', 'get_session_ble')
class BettercapGetSessionBleCommand(BettercapGetCommand):
    cmd: Literal['get_session_ble']


@CommandRegistry.register('bettercap', 'get_session_interface')
class BettercapGetSessionInterfaceCommand(BettercapGetCommand):
    cmd: Literal['get_session_interface']


@CommandRegistry.register('bettercap', 'get_session_lan')
class BettercapGetSessionLanCommand(BettercapGetCommand):
    cmd: Literal['get_session_lan']


@CommandRegistry.register('bettercap', 'get_session_options')
class BettercapGetSessionOptionsCommand(BettercapGetCommand):
    cmd: Literal['get_session_options']


@CommandRegistry.register('bettercap', 'get_session_packets')
class BettercapGetSessionPacketsCommand(BettercapGetCommand):
    cmd: Literal['get_session_packets']


@CommandRegistry.register('bettercap', 'get_session_started_at')
class BettercapGetSessionStartedAtCommand(BettercapGetCommand):
    cmd: Literal['get_session_started_at']


@CommandRegistry.register('bettercap', 'get_session_wifi')
class BettercapGetSessionWifiCommand(BettercapGetCommand):
    cmd: Literal['get_session_wifi']


"""
  Please note that get_file() needs a parameter and
  therefor it is not a BettercapGetCommand!
"""


@CommandRegistry.register('bettercap', 'get_file')
class BettercapGetFileCommand(BaseCommand):
    cmd: Literal['get_file']
    type: Literal['bettercap']
    filename: str
    connection: Optional[str] = None


@CommandRegistry.register('bettercap', 'post_api_session')
class BettercapPostApiSessionCommand(BaseCommand):
    cmd: Literal['post_api_session']
    type: Literal['bettercap']
    data: Optional[Dict[str, Any]] = None
    connection: Optional[str] = None


@CommandRegistry.register('bettercap', 'delete_api_events')
class BettercapDeleteApiEventsCommand(BaseCommand):
    cmd: Literal['delete_api_events']
    type: Literal['bettercap']
    connection: Optional[str] = None
