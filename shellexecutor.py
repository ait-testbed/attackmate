import subprocess
from baseexecutor import BaseExecutor, Result


class ShellExecutor(BaseExecutor):

    def _exec_cmd(self, command):
        result = subprocess.run(command.cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        return Result(result.stdout.decode(), result.returncode)
