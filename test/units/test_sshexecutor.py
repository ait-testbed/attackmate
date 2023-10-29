from paramiko.client import SSHClient
from attackmate.schemas import SSHCommand
from attackmate.variablestore import VariableStore
from attackmate.sshexecutor import SSHExecutor


class TestSSHExecutor:
    def test_ssh_connection(self, mocker):
        varstore = VariableStore()
        cmd = SSHCommand(hostname="192.168.22.10", username="root", cmd="id", type="ssh")
        ssh = SSHExecutor(varstore=varstore)
        ssh.cache_settings(cmd)
        mocker.patch(
            'paramiko.SSHClient.connect',
            return_value=False
        )
        assert isinstance(ssh.connect_use_session(cmd), SSHClient)
