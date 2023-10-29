class Result:
    """

    Instances of this Result-class will be returned
    by the Executors. It stores the standard-output
    and the returncode.
    """
    stdout: str
    returncode: int

    def __init__(self, stdout, returncode):
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
        """
        self.stdout = stdout
        self.returncode = returncode
