"""
msfpayloadexecutor
============================================
This class enables generating metasploit
payloads in AttackMate.
"""

import tempfile
from typing import Any, Dict
from pymetasploit3.msfrpc import MsfRpcClient
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.result import Result
from attackmate.execexception import ExecException
from attackmate.processmanager import ProcessManager
from attackmate.variablestore import VariableStore
from attackmate.executors.features.cmdvars import CmdVars
from attackmate.schemas.metasploit import MsfPayloadCommand
from attackmate.schemas.config import CommandConfig, MsfConfig
from attackmate.executors.metasploit.msfclientmixin import MsfClientMixin
from attackmate.executors.executor_factory import executor_factory


@executor_factory.register_executor('msf-payload')
class MsfPayloadExecutor(MsfClientMixin, BaseExecutor):
    def __init__(
        self, pm: ProcessManager, varstore: VariableStore, cmdconfig=CommandConfig(), *,
        msf_config: Dict[str, MsfConfig] = {}
    ):
        self.msf_config = msf_config
        self._msf_clients: Dict[str, MsfRpcClient] = {}
        self.tempfilestore: list[Any] = []
        super().__init__(pm, varstore, cmdconfig)

    def log_command(self, command: MsfPayloadCommand):
        self.logger.info(f"Generating Msf-Payload: '{command.cmd}'")

    def prepare_payload(self, command: MsfPayloadCommand, msf: MsfRpcClient):
        payload = msf.modules.use('payload', command.cmd)
        payload.runoptions['BadChars'] = command.badchars
        payload.runoptions['Encoder'] = command.encoder
        payload.runoptions['Format'] = command.format
        payload.runoptions['NopSledSize'] = CmdVars.variable_to_int('nopsled_size', command.nopsled_size)
        payload.runoptions['ForceEncode'] = command.force_encode
        if command.template:
            payload.runoptions['Template'] = command.template
            payload.runoptions['KeepTemplateWorking'] = command.keep_template_working
        if command.platform:
            payload.runoptions['Platform'] = command.platform
        payload.runoptions['Iterations'] = CmdVars.variable_to_int('iter', command.iter)

        for option, setting in command.payload_options.items():
            try:
                payload[option] = setting
            except KeyError:
                raise ExecException(f'Payload option {option} is unknown')
        return payload

    def get_local_path(self, command: MsfPayloadCommand):
        payload_path = None
        if command.local_path:
            payload_path = command.local_path
        else:
            tmpfile = tempfile.NamedTemporaryFile()
            self.tempfilestore.append(tmpfile)
            payload_path = tmpfile.name
        return payload_path

    async def _exec_cmd(self, command: MsfPayloadCommand) -> Result:
        conn_name = self._resolve_connection(command)
        msf = self._get_client(conn_name)

        payload = self.prepare_payload(command, msf)
        try:
            data = payload.payload_generate()
        except Exception:
            raise ExecException('Incorrect payload settings. Did you forget any options?')

        payload_path = self.get_local_path(command)

        try:
            with open(payload_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            raise ExecException(f'Unable to write file: {e}')

        self.varstore.set_variable('LAST_MSF_PAYLOAD', payload_path)
        return Result(f'Payload saved to {payload_path}', 0)
