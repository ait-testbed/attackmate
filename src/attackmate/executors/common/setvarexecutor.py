"""
setvarexecutor.py
============================================
This class allows to set variables.
"""

from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.schemas.setvar import SetVarCommand
import base64
import codecs
import urllib.parse


class SetVarExecutor(BaseExecutor):
    def encode(self, encoder: str, cmd: str):
        if encoder == 'base64-encoder':
            return base64.b64encode(bytes(cmd, 'utf-8')).decode('utf-8')
        elif encoder == 'base64-decoder':
            return base64.b64decode(bytes(cmd, 'utf-8')).decode('utf-8')
        elif encoder == 'rot13':
            return codecs.encode(cmd, 'rot-13')
        elif encoder == 'urlencoder':
            return urllib.parse.quote(cmd, safe='')
        elif encoder == 'urldecoder':
            return urllib.parse.unquote(cmd)
        else:
            return cmd

    def log_command(self, command: SetVarCommand):
        self.logger.warning(f"Setting Variable: '{command.variable}'")

    def _exec_cmd(self, command: SetVarCommand) -> Result:
        self.setoutuptvars = False
        content = command.cmd
        if command.encoder:
            try:
                content = self.encode(command.encoder, command.cmd)
            except Exception as e:
                self.logger.warning(f'Encoding failed. Fallback to plain: {e}')
        self.varstore.set_variable(command.variable, content)

        return Result('', 0)
