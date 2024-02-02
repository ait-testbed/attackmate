import re
import logging
from attackmate.result import Result
from attackmate.schemas.base import BaseCommand


class ExitOnError:
    def __init__(self):
        self.logger = logging.getLogger('playbook')

    def exit_on_error(self, command: BaseCommand, result: Result):
        if result.returncode != 0 and command.exit_on_error:
            self.logger.error(result.stdout)
            self.logger.debug('Exiting because return-code is not 0')
            exit(1)

    def error_if_or_not(self, command: BaseCommand, result: Result):
        self.error_if(command, result)
        self.error_if_not(command, result)

    def error_if(self, command: BaseCommand, result: Result):
        if command.error_if is not None:
            m = re.search(command.error_if, result.stdout, re.MULTILINE)
            if m is not None:
                self.logger.error(
                        f'Exitting because error_if matches: {m.group(0)}'
                        )
                exit(1)

    def error_if_not(self, command: BaseCommand, result: Result):
        if command.error_if_not is not None:
            m = re.search(command.error_if_not, result.stdout, re.MULTILINE)
            if m is None:
                self.logger.error(
                        'Exitting because error_if_not does not match'
                        )
                exit(1)
