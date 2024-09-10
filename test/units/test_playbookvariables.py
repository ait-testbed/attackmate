import os
import pytest
from unittest.mock import patch

from attackmate.playbook_env_var_replacer import replace_env_variables_in_playbook

sample_playbook = """\
vars:
    PLAYBOOK_VAR: 102.49.20.00
    $SECOND_PLAYBOOK_VAR: foo
commands:
    - type: debug
      cmd: echo $ENVIRONMENT_VAR
    - type: debug
      cmd: echo $PLAYBOOK_VAR
    - type: debug
      cmd: echo $SECOND_PLAYBOOK_VAR
"""


def test_replace_env_variables():
    env_vars = {'ENVIRONMENT_VAR': 'bar'}
    with patch.dict(os.environ, env_vars):
        expected_result = """\
vars:
    PLAYBOOK_VAR: 102.49.20.00
    $SECOND_PLAYBOOK_VAR: foo
commands:
    - type: debug
      cmd: echo bar
    - type: debug
      cmd: echo $PLAYBOOK_VAR
    - type: debug
      cmd: echo $SECOND_PLAYBOOK_VAR
"""
        assert replace_env_variables_in_playbook(sample_playbook) == expected_result


def test_no_env_variable_set():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Environment variable 'ENVIRONMENT_VAR' is not set"):
            replace_env_variables_in_playbook(sample_playbook)


def test_no_vars_section():
    playbook_without_vars = """\
commands:
    - type: debug
      cmd: echo $ENVIRONMENT_VAR
    - type: debug
      cmd: echo $ENVIRONMENT_VAR_2
"""
    env_vars = {'ENVIRONMENT_VAR': 'bar', 'ENVIRONMENT_VAR_2': 'bar_2'}
    with patch.dict(os.environ, env_vars):
        expected_result = """\
commands:
    - type: debug
      cmd: echo bar
    - type: debug
      cmd: echo bar_2
"""
        assert replace_env_variables_in_playbook(playbook_without_vars) == expected_result


def test_no_replacement_needed():
    playbook_without_env_vars_to_replace = """\
vars:
    PLAYBOOK_VAR: 102.49.20.00
    $PLAYBOOK_VAR_WITH_LEADING_DOLLAR_SIGN: foo
    $PLAYBOOK_VAR_WITH_NUMBER_1: bar
commands:
    - type: debug
      cmd: echo $PLAYBOOK_VAR
    - type: debug
      cmd: echo $PLAYBOOK_VAR_WITH_LEADING_DOLLAR_SIGN
    - type: debug
      cmd: echo $PLAYBOOK_VAR_WITH_NUMBER_1
"""
    assert (
        replace_env_variables_in_playbook(playbook_without_env_vars_to_replace)
        == playbook_without_env_vars_to_replace
    )


def test_ignore_vars_section_variables():
    # test that variables names defind in var-section take precedence over env vars
    playbook_with_ignored_env_vars = """\
vars:
    $IGNORED_VAR: some_value
commands:
    - type: debug
      cmd: echo $IGNORED_VAR
"""
    env_vars = {'IGNORED_VAR': 'should_not_replace'}
    with patch.dict(os.environ, env_vars):
        assert (
            replace_env_variables_in_playbook(playbook_with_ignored_env_vars)
            == playbook_with_ignored_env_vars
        )


def test_vars_section_variable_value_is_env_var():
    # Test that a $VALUE in the vars section is replaced by environment variables
    playbook_with_env_var_value = """\
vars:
    PLAYBOOK_VAR: $ENV_VAR_AS_VALUE_IN_VARS_SECTION
commands:
    - type: debug
      cmd: echo $PLAYBOOK_VAR
"""
    env_vars = {'ENV_VAR_AS_VALUE_IN_VARS_SECTION': 'FOO', 'PLAYBOOK_VAR': 'SHOULD_NOT_REPLACE'}
    with patch.dict(os.environ, env_vars):
        expected_result = """\
vars:
    PLAYBOOK_VAR: FOO
commands:
    - type: debug
      cmd: echo $PLAYBOOK_VAR
"""
        assert replace_env_variables_in_playbook(playbook_with_env_var_value) == expected_result


def test_vars_section_variable_value_is_capitalized():
    # Test that capitalized value in the vars section is not replaced by environment variables
    playbook_with_env_var_value = """\
vars:
    PLAYBOOK_VAR: FOO
commands:
    - type: debug
      cmd: echo $PLAYBOOK_VAR
"""
    env_vars = {'FOO': 'SHOULD_NOT_REPLACE', 'PLAYBOOK_VAR': 'SHOULD_NOT_REPLACE'}
    with patch.dict(os.environ, env_vars):
        assert replace_env_variables_in_playbook(playbook_with_env_var_value) == playbook_with_env_var_value


def test_vars_section_variable_with_prefix():
    # Test that prefixed variable is not replaced if no env var exists
    playbook_with_env_var_value = """\
vars:
    ATTACKMATE_FOO: FOO
commands:
    - type: debug
      cmd: echo $ATTACKMATE_FOO
"""

    assert replace_env_variables_in_playbook(playbook_with_env_var_value) == playbook_with_env_var_value


def test_vars_section_variable_with_prefix_gets_replaced():
    # Test that prefixed variable is replaced if env var exists
    playbook_with_env_var_value = """\
vars:
    ATTACKMATE_FOO: foo
commands:
    - type: debug
      cmd: echo $ATTACKMATE_FOO
"""
    env_vars = {'FOO': 'env_foo'}
    with patch.dict(os.environ, env_vars):
        expected_result = """\
vars:
    ATTACKMATE_FOO: foo
commands:
    - type: debug
      cmd: echo env_foo
"""
        assert replace_env_variables_in_playbook(playbook_with_env_var_value) == expected_result


def test_var_and_env_var_with_same_name():
    # Test that prefixed variable is replaced if env var exists, but unprefixed var is not replaced
    playbook_with_env_var_value = """\
vars:
    ATTACKMATE_FOO: foo
    SAME_NAME_IN_VAR_SECTION_AND_ENV: bar
commands:
    - type: debug
      cmd: echo $ATTACKMATE_FOO $SAME_NAME_IN_VAR_SECTION_AND_ENV
"""
    env_vars = {'FOO': 'env_foo'}
    with patch.dict(os.environ, env_vars):
        expected_result = """\
vars:
    ATTACKMATE_FOO: foo
    SAME_NAME_IN_VAR_SECTION_AND_ENV: bar
commands:
    - type: debug
      cmd: echo env_foo $SAME_NAME_IN_VAR_SECTION_AND_ENV
"""
        assert replace_env_variables_in_playbook(playbook_with_env_var_value) == expected_result


def test_env_var_with_prefix():
    # Test that env variable with ATTACKACKMATE prefix is replaced
    # if that variable is not defined in vars section
    playbook_with_env_var_value = """\
vars:
    ATTACKMATE_FOO: foo
commands:
    - type: debug
      cmd: echo $ATTACKMATE_PREFIXED_VAR_NOT_DEFINED_IN_VAR_SECTION
"""
    env_vars = {'ATTACKMATE_PREFIXED_VAR_NOT_DEFINED_IN_VAR_SECTION': 'env_bar'}
    with patch.dict(os.environ, env_vars):
        expected_result = """\
vars:
    ATTACKMATE_FOO: foo
commands:
    - type: debug
      cmd: echo env_bar
"""
        assert replace_env_variables_in_playbook(playbook_with_env_var_value) == expected_result
