class Result:
    """

    Instances of this Result-class will be returned
    by the Executors. It stores the standard-output
    and the returncode.
    """
    stdout: str
    returncode: int

    def __init__(self, stdout, returncode, exit_status=None):
        """ Constructor of the Result

        Instances of this Result-class will be returned
        by the Executors. It stores the standard-output
        and the returncode.

        Parameters
        ----------
        stdout : str
            The standard-output of a command.
        returncode : int
            The returncode of a previous executed command
        exit_status : int, optional
            The real exit status of the process, where one genuinely exists.
            ``returncode`` is what drives ``exit_on_error`` and stays at its
            historical value unless a command opts in with ``use_exit_code``;
            this field is what gets recorded in the JSON audit log, and is
            ``None`` when no true status is available - inside a live session
            the shell is still running, so there is nothing to report.
        """
        self.stdout = stdout
        self.returncode = returncode
        self.exit_status = exit_status

    def __repr__(self):
        return (f'Result(stdout={repr(self.stdout)}, returncode={self.returncode}, '
                f'exit_status={self.exit_status})')
