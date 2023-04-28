import re
import time


class Result:
    stdout: str
    returncode: int

    def __init__(self, stdout, returncode):
        self.stdout = stdout
        self.returncode = returncode


class BaseExecutor:
    def __init__(self, logger, cmdconfig=None):
        self.logger = logger
        self.cmdconfig = cmdconfig
        self.logger.debug(self.cmdconfig)

    def run(self, command):
        self.run_count = 1
        self.exec(command)

    def exec(self, command):
        self.logger.info(f"Running shellcommand: '{command}'")
        result = self._exec_cmd(command)
        self.logger.info(result.stdout)
        self.error_if(command, result)
        self.error_if_not(command, result)
        self.loop_if(command, result)
        self.loop_if_not(command, result)

    def error_if(self, command, result):
        if command.error_if is not None:
            m = re.search(command.error_if, result.stdout, re.MULTILINE)
            if m is not None:
                self.logger.error(
                        f"Exitting because error_if matches: {m.group(0)}"
                        )
                exit(1)

    def error_if_not(self, command, result):
        if command.error_if_not is not None:
            m = re.search(command.error_if_not, result.stdout, re.MULTILINE)
            if m is None:
                self.logger.error(
                        "Exitting because error_if_not does not match"
                        )
                exit(1)

    def loop_if(self, command, result):
        if command.loop_if is not None:
            m = re.search(command.loop_if, result.stdout, re.MULTILINE)
            if m is not None:
                self.logger.error(
                        f"Re-run command because loop_if matches: {m.group(0)}"
                        )
                if self.run_count < command.loop_count:
                    self.run_count = self.run_count + 1
                    time.sleep(self.cmdconfig.loop_sleep)
                    self.exec(command)
                else:
                    self.logger.error("Exitting because loop_count exceeded")
                    exit(1)

    def loop_if_not(self, command, result):
        if command.loop_if_not is not None:
            m = re.search(command.loop_if_not, result.stdout, re.MULTILINE)
            if m is None:
                self.logger.error(
                        "Re-run command because loop_if_not does not match"
                        )
                if self.run_count < command.loop_count:
                    self.run_count = self.run_count + 1
                    time.sleep(self.cmdconfig.loop_sleep)
                    self.exec(command)
                else:
                    self.logger.error("Exitting because loop_count exceeded")
                    exit(1)

    def _exec_cmd(self, command):
        return Result
