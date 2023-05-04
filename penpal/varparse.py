class VarParse:
    def __init__(self, variables):
        self.variables = variables

    def parse_command(self, cmd):
        if type(self.variables) == dict:
            for k, v in self.variables.items():
                cmd = cmd.replace(k, v)
        return cmd
