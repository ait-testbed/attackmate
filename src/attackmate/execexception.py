class ExecException(Exception):
    """ Exception for all Executors

    This exception is raised by Executors if anything
    goes wrong. The BaseExecutor will catch the
    Exception, writes it to the console and exits
    gracefully.

    """
    pass
