from typing import Annotated, List, Optional
from pydantic import AfterValidator, BeforeValidator, BaseModel, ValidationInfo
import re

# https://stackoverflow.com/questions/71539448/using-different-pydantic-models-depending-on-the-value-of-fields
VAR_PATTERN = r'^\$[$a-zA-Z0-9_]+$|^[0-9]+$'
pattern = re.compile(VAR_PATTERN)


def transform_int_to_str(value) -> str:
    return str(value)


def check_var_pattern(value: str, info: ValidationInfo) -> str:
    global pattern
    assert pattern.match(value), f'{info.field_name} must be a variable, integer or numeric string'
    return value


StringNumber = Annotated[Optional[str | int],
                         BeforeValidator(transform_int_to_str),
                         AfterValidator(check_var_pattern)]

# Like StringNumber but without checks for valid $variable
StrInt = Annotated[Optional[str | int], BeforeValidator(transform_int_to_str)]

class BaseCommand(BaseModel):
    def list_template_vars(self) -> List[str]:
        """ Get a list of all variables that can be used as templates

        Returns a List with all member-names that can be used as
        templates for the VariableStore. Basically all members
        can be used that are strings where the value is not None.
        The member "type" is explicitly excluded.

        Returns
        -------
        List[str]
            List with names of all member-variables
        """
        template_vars: List[str] = []
        for k in self.__dict__.keys():
            tmp = getattr(self, k)
            if isinstance(tmp, (str, dict, list)) and k != 'type':
                template_vars.append(k)
        return template_vars

    only_if: Optional[str] = None
    error_if: Optional[str] = None
    error_if_not: Optional[str] = None
    loop_if: Optional[str] = None
    loop_if_not: Optional[str] = None
    loop_count: StringNumber = '3'
    exit_on_error: bool = True
    save: Optional[str] = None
    cmd: str
    background: bool = False
    kill_on_exit: bool = True
