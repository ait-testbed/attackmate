import os
import re


def replace_env_variables_in_playbook(content: str) -> str:
    """Replaces environment variables in the content with their actual values.
    First parses the variable names in the playbook vars section (between
    "vars:" and "commands:"), and saves them in a set. Variablenames defined
    in the vars section will only be replaced by environmental variables values
    if they are prefixed with ATTACKMATE_, and only if the env variable (
    without the attackmate prefix) exists

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
    var_pattern = re.compile(r'\$([A-Z_0-9]+)')
    # Regex to find variable names in the vars section, with or without leading $, followed by ": value"
    vars_section_var_pattern = re.compile(r'^\s*\$?([A-Z_0-9]+)(?=\: ?.+$)', re.MULTILINE)

    # find the vars section
    vars_section_match = playbook_vars_section_pattern.search(content)
    if vars_section_match:
        vars_section = vars_section_match.group(1)
        # find all variables in the vars section
        vars_section_var_names = set(vars_section_var_pattern.findall(vars_section))
        # filter for variables in the vars section prefixed with ATTACKMATE_
        vars_section_var_names_with_attackmate_prefix = {
            var for var in vars_section_var_names if var.startswith('ATTACKMATE_')
        }
    else:
        vars_section_var_names = set()
        vars_section_var_names_with_attackmate_prefix = set()

    def replace_variable(match):
        variable_name = match.group(1)

        # Do not replace if it is a variable name from the vars section not prefixed with ATTACKMATE_
        if (
            variable_name in vars_section_var_names
            and variable_name not in vars_section_var_names_with_attackmate_prefix
        ):
            return f'${variable_name}'

        if variable_name in vars_section_var_names_with_attackmate_prefix:
            # Remove the ATTACKMATE_ prefix from the variable name
            env_var_name = variable_name[len('ATTACKMATE_') :]

            # Check if the environment variable without the prefix exists
            value = os.getenv(env_var_name)

            # If it exists, return its value, otherwise return the variable name with the prefix
            return value if value is not None else f'${variable_name}'

        # Otherwise replace with env variable value
        value = os.getenv(variable_name)
        if value is None:
            raise ValueError(f"Environment variable '{variable_name}' is not set")
        return value

    # Replace variables in the playbook
    new_content = var_pattern.sub(replace_variable, content)
    return new_content
