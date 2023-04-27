import schemas
import subprocess

class ShellExecutor:
    def __init__(self, logger):
        self.logger = logger

    def exec(self, command):
        self.logger.info(f"Running shellcommand: '{command.cmd}'")
        result = subprocess.run(command.cmd, shell=True, capture_output=True)
        print(result)
        self.logger.info(result.stdout.decode())
