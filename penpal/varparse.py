class VarParse:
    def __init__(self, variables):
        self.variables = variables

    def parse_command(self, parse_str):
        if type(self.variables) == dict:
            for k, v in self.variables.items():
                parse_str = parse_str.replace(k, v)
        return parse_str
