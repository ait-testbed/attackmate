import os
import re


def replace_env_variables_in_playbook(content: str) -> str:
    """Replaces environment variables in the content with their actual values.
    First parses the variable names in the playbook vars section (between
    "vars:" and "commands:"), and saves them in a set. The variables from the vars
    section will not be replaced by environmental variables anywhere in the playbook.

    ## Sample playbook ##
    vars:
        PLAYBOOK_VAR: 102.49.20.00
        $SECOND_PLAYBOOK_VAR: foo
    commands:
        - type: debug
          cmd: echo $ENVIRONMENT_VAR # gets replaced by corresponding env var
        - type: debug
          cmd: echo $PLAYBOOK_VAR
        - type: debug
          cmd: echo $SECOND_PLAYBOOK_VAR

    Parameters
    ----------
    content : str
        The content of the playbook file.

    Returns
    -------
    str
        The content of the playbook file with environment variables replaced.
    """
    # Regex to find the "vars:" section of the playbook
    playbook_vars_section_pattern = re.compile(r'vars:\s*(.*?)\s*commands:', re.DOTALL)
    # Regex to find variables in the format $SOME_VARIABLE
    var_pattern = re.compile(r'\$([A-Z_]+)')
    # Regex to find variable names in the vars section, with or without the leading $, followed by ':'
    vars_section_var_pattern = re.compile(r'^\s*\$?([A-Z_]+)(?=:)', re.MULTILINE)

    # find the vars section
    vars_section_match = playbook_vars_section_pattern.search(content)
    if vars_section_match:
        vars_section = vars_section_match.group(1)
        # find all variables in the vars section
        vars_section_var_names = set(vars_section_var_pattern.findall(vars_section))
    else:
        vars_section_var_names = set()

    def replace_variable(match):
        variable_name = match.group(1)

        # Do not replace if it is a variable name from the vars section
        if variable_name in vars_section_var_names:
            return f'${variable_name}'

        # Otherwise replace with env variable value
        value = os.getenv(variable_name)
        if value is None:
            raise ValueError(f"Environment variable '{variable_name}' is not set")
        return value

    # Replace variables in the playbook
    new_content = var_pattern.sub(replace_variable, content)
    return new_content
