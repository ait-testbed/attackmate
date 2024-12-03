import os
from attackmate.execexception import ExecException
from attackmate.schemas.ssh import SFTPCommand
from paramiko.client import SSHClient


class SFTPFeature:
    def exec_sftp(self, client: SSHClient, command: SFTPCommand) -> str:
        output = ''
        if command.cmd == 'put':
            try:
                client.open_sftp().put(command.local_path, command.remote_path)
                output = f'Uploaded to {command.remote_path}'
                if command.mode:
                    client.open_sftp().chmod(command.remote_path, int(command.mode, 8))
            except IOError as e:
                raise ExecException(
                    f'Could not upload to {command.remote_path}. '
                    f'Ensure that the destination path specifies a filename. '
                    f'Original IOError: {e}'
                )
        elif command.cmd == 'get':
            client.open_sftp().get(command.remote_path, command.local_path)
            output = f'Downloaded from {command.remote_path}'
            if command.mode:
                os.chmod(command.local_path, int(command.mode, 8))
        return output
