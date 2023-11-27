import os
from attackmate.schemas.ssh import SFTPCommand
from paramiko.client import SSHClient


class SFTPFeature():
    def exec_sftp(self, client: SSHClient, command: SFTPCommand) -> str:
        output = ''
        if command.cmd == 'put':
            client.open_sftp().put(command.local_path, command.remote_path)
            output = f'Uploaded to {command.remote_path}'
            if command.mode:
                client.open_sftp().chmod(command.remote_path, int(command.mode, 8))
        elif command.cmd == 'get':
            client.open_sftp().get(command.remote_path, command.local_path)
            output = f'Downloaded from {command.remote_path}'
            if command.mode:
                os.chmod(command.local_path, int(command.mode, 8))
        return output
