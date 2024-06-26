import pytest
from pydantic import ValidationError
from attackmate.schemas.regex import RegExCommand


class TestRegExCommand:
    def test_sub_needs_replace_valid(self):
        # Test when mode is 'sub' and replace is provided
        command = RegExCommand(type='regex', cmd='test', mode='sub', replace='some_replace', output={})
        assert command.mode == 'sub'
        assert command.replace == 'some_replace'

    def test_sub_needs_replace_invalid(self):
        # Test when mode is 'sub' but replace is not provided
        with pytest.raises(ValueError, match='Regex sub mode needs replace-setting!'):
            RegExCommand(type='regex', cmd='test', mode='sub', output={})

    def test_default_values(self):
        # Test default values for other attributes
        command = RegExCommand(type='regex', cmd='test', output={})
        assert command.mode == 'findall'
        assert command.input == 'RESULT_STDOUT'
        assert command.replace is None
        assert command.output == {}

    def test_missing_cmd_argument(self):
        # Test for missing 'cmd' argument
        with pytest.raises(ValidationError, match='1 validation error for RegExCommand'):
            RegExCommand(type='regex', output={})
