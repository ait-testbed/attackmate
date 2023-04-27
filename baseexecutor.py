import re


class VarParse:
    def __init__(self, variables):
        self.variables = variables

    def parse(self, command):
        for k, v in self.variables:
            command = command.replace(k, v)
        return command


class Result:
    stdout: str
    returncode: int

    def __init__(self, stdout, returncode):
        self.stdout = stdout
        self.returncode = returncode


class BaseExecutor:
    def __init__(self, logger):
        self.logger = logger

    def exec(self, command):
        self.logger.info(f"Running shellcommand: '{command}'")
        result = self._exec(command)
        self.logger.info(result.stdout)
        self.error_if(command, result)

    def error_if(self, command, result):
        if command.error_if is not None:
            m = re.search(command.error_if, result.stdout, re.MULTILINE)
            if m is not None:
                self.logger.error(f"error_if matches: {m.group(0)}")
                exit(1)

    def _exec(self, command):
        return Result
