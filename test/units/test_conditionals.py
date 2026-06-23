import pytest
from attackmate.executors.features.conditional import Conditional, ConditionalError


class TestConditionals:

    def test_variable_only(self):
        assert Conditional.test('variable')
        assert Conditional.test('') is False
        assert Conditional.test(None) is False
        assert Conditional.test('1')
        assert Conditional.test('0') is False
        assert Conditional.test('False') is False
        assert Conditional.test('True')
        with pytest.raises(SyntaxError):
            Conditional.test('-')
        with pytest.raises(SyntaxError):
            Conditional.test('!')
        with pytest.raises(SyntaxError):
            Conditional.test('$')
        with pytest.raises(SyntaxError):
            Conditional.test('$test')
        with pytest.raises(SyntaxError):
            Conditional.test('not')
        with pytest.raises(SyntaxError):
            Conditional.test('a=b')
        with pytest.raises(SyntaxError):
            Conditional.test('a=1')

    def test_negate_variable(self):
        assert Conditional.test('not 0')
        assert Conditional.test('not 1') is False
        assert Conditional.test('not alibert') is False
        with pytest.raises(SyntaxError):
            assert Conditional.test('! 0')

    def test_compare(self):
        assert Conditional.test('a == a')
        assert Conditional.test('a == b') is False
        assert Conditional.test('a != b')
        assert Conditional.test('1 == 1')
        assert Conditional.test('1 == 2') is False
        assert Conditional.test('1 == True')
        assert Conditional.test('0 == False')
        assert Conditional.test('1 < 10')
        assert Conditional.test('10 < 1') is False
        assert Conditional.test('10 <= 1') is False
        assert Conditional.test('10 > 1')
        assert Conditional.test('10 >= 1')
        assert Conditional.test('1 >= 10') is False
        assert Conditional.test('1 > 10') is False
        assert Conditional.test('test is test')
        assert Conditional.test('apple is not banana')
        assert Conditional.test('1 is True') is False
        assert Conditional.test('1 == True')
        assert Conditional.test('0 == True') is False
        assert Conditional.test('2 == True') is False

    def test_exceptions(self):
        with pytest.raises(ConditionalError, match='Unknown Condition:'):
            Conditional.test('{"a":1, **d}')
        with pytest.raises(ConditionalError, match='Unknown right-operand'):
            Conditional.test('a > ( a + b)')
        with pytest.raises(ConditionalError, match='Unknown left-operand'):
            Conditional.test('( a + b) < c')
        with pytest.raises(ConditionalError, match="Unknown expression operand in 'not'"):
            Conditional.test('not (a + b)')
        with pytest.raises(ConditionalError, match='Unknown compare operation'):
            Conditional.test('a in b')

    def test_regex(self):
        # exact matches
        assert Conditional.test('foo =~ foo') is True
        assert Conditional.test('foo =~ bar') is False
        assert Conditional.test('foo !~ foo') is False
        assert Conditional.test('foo !~ bar') is True

        assert Conditional.test('foo =~ foo') is True
        assert Conditional.test('foo =~ bar') is False
        assert Conditional.test('foo !~ foo') is False
        assert Conditional.test('foo !~ bar') is True

        # matches somewhere in the string
        assert Conditional.test('somethingfoo =~ foo') is True
        assert Conditional.test('foosomething =~ bar') is False
        assert Conditional.test('somehtingfoo !~ foo') is False
        assert Conditional.test('foosomething !~ bar') is True

        # matches with wildcards and ranges
        assert Conditional.test('hello =~ h.llo') is True  # Single character wildcard
        assert Conditional.test('hello =~ h.*o') is True  # Zero or more characters
        assert Conditional.test('hello =~ h[aeiou]llo') is True  # Character set
        assert Conditional.test('hello =~ h[^aeiou]llo') is False  # Negated character set
        assert Conditional.test('hello123 =~ h.*\\d+') is True  # Digits
        assert Conditional.test('hello =~ ^h.*o$') is True  # Start and end of string

        assert Conditional.test('hello !~ h.llo') is False
        assert Conditional.test('hello !~ h.*o') is False
        assert Conditional.test('hello !~ h[aeiou]llo') is False
        assert Conditional.test('hello !~ h[^aeiou]llo') is True
        assert Conditional.test('hello123 !~ h.*\\d+') is False
        assert Conditional.test('hello !~ ^h.*o$') is False


class TestConditionalStringComparisons:
    """Test conditional evaluations with string values"""

    def test_string_equality_with_quotes(self):
        """Test string equality: VAR == "hello" """
        # When variables are substituted, 'hello' becomes the Name 'hello'
        # and "hello" is a Constant string
        assert Conditional.test('hello == "hello"') is True
        assert Conditional.test('hello == "world"') is False

    def test_string_equality_without_quotes(self):
        """Test string equality: VAR == hello (both Names)"""
        assert Conditional.test('hello == hello') is True
        assert Conditional.test('hello == world') is False

    def test_string_inequality(self):
        """Test string inequality: VAR != "hello" """
        assert Conditional.test('hello != "world"') is True
        assert Conditional.test('hello != "hello"') is False

    def test_string_comparison_less_than(self):
        """Test string comparison: VAR < "world" """
        assert Conditional.test('"apple" < "banana"') is True
        assert Conditional.test('"zebra" < "apple"') is False

    def test_string_comparison_greater_than(self):
        """Test string comparison: VAR > "world" """
        assert Conditional.test('"zebra" > "apple"') is True
        assert Conditional.test('"apple" > "zebra"') is False

    def test_string_comparison_less_than_or_equal(self):
        """Test string comparison: VAR <= "world" """
        assert Conditional.test('"apple" <= "banana"') is True
        assert Conditional.test('"apple" <= "apple"') is True
        assert Conditional.test('"zebra" <= "apple"') is False

    def test_string_comparison_greater_than_or_equal(self):
        """Test string comparison: VAR >= "world" """
        assert Conditional.test('"zebra" >= "apple"') is True
        assert Conditional.test('"zebra" >= "zebra"') is True
        assert Conditional.test('"apple" >= "zebra"') is False


class TestConditionalIntegerComparisons:
    """Test conditional evaluations with integer values"""

    def test_integer_equality(self):
        """Test integer equality: VAR == 123"""
        assert Conditional.test('123 == 123') is True
        assert Conditional.test('123 == 456') is False

    def test_integer_inequality(self):
        """Test integer inequality: VAR != 123"""
        assert Conditional.test('123 != 456') is True
        assert Conditional.test('123 != 123') is False

    def test_integer_less_than(self):
        """Test integer comparison: VAR < 100"""
        assert Conditional.test('50 < 100') is True
        assert Conditional.test('150 < 100') is False

    def test_integer_greater_than(self):
        """Test integer comparison: VAR > 100"""
        assert Conditional.test('150 > 100') is True
        assert Conditional.test('50 > 100') is False

    def test_integer_less_than_or_equal(self):
        """Test integer comparison: VAR <= 100"""
        assert Conditional.test('50 <= 100') is True
        assert Conditional.test('100 <= 100') is True
        assert Conditional.test('150 <= 100') is False

    def test_integer_greater_than_or_equal(self):
        """Test integer comparison: VAR >= 100"""
        assert Conditional.test('150 >= 100') is True
        assert Conditional.test('100 >= 100') is True
        assert Conditional.test('50 >= 100') is False

    def test_integer_boolean_equality(self):
        """Test integer-boolean equality (Python's behavior: 1 == True, 0 == False)"""
        assert Conditional.test('1 == True') is True
        assert Conditional.test('0 == False') is True
        assert Conditional.test('2 == True') is False


class TestConditionalMixedTypes:
    """Test conditional evaluations with mixed types"""

    def test_string_number_inequality(self):
        """Test that string "123" is not equal to integer 123"""
        assert Conditional.test('"123" == 123') is False
        assert Conditional.test('"123" != 123') is True

    def test_numeric_string_equality(self):
        """Test numeric string equality"""
        assert Conditional.test('"123" == "123"') is True
        assert Conditional.test('"123" != "456"') is True


class TestConditionalRegex:
    """Test conditional regex matching"""

    def test_regex_match(self):
        """Test regex match: string =~ pattern"""
        assert Conditional.test('hello =~ h.*o') is True
        assert Conditional.test('hello =~ ^hell') is True
        assert Conditional.test('hello =~ world') is False

    def test_regex_not_match(self):
        """Test regex not match: string !~ pattern"""
        assert Conditional.test('hello !~ world') is True
        assert Conditional.test('hello !~ ^hell') is False

    def test_regex_with_numbers(self):
        """Test regex with numeric strings"""
        assert Conditional.test('123 =~ ^[0-9]+$') is True
        assert Conditional.test('hello123 =~ [0-9]+') is True
        assert Conditional.test('hello =~ ^[0-9]+$') is False


class TestConditionalBoolean:
    """Test conditional boolean evaluations"""

    def test_truthy_variable(self):
        """Test truthy variable evaluation (Names are truthy)"""
        assert Conditional.test('true') is True
        assert Conditional.test('True') is True

    def test_not_operator(self):
        """Test not operator"""
        assert Conditional.test('not False') is True
        assert Conditional.test('not True') is False

    def test_constant_true(self):
        """Test constant True evaluation"""
        assert Conditional.test('True') is True

    def test_constant_false(self):
        """Test constant False evaluation"""
        assert Conditional.test('False') is False

    def test_empty_or_none(self):
        """Test empty/None conditions"""
        assert Conditional.test(None) is False
        assert Conditional.test('') is False


class TestConditionalIsOperator:
    """Test conditional 'is' and 'is not' operators"""

    def test_is_operator_with_none(self):
        """Test 'is' operator with None"""
        assert Conditional.test('None is None') is True

    def test_is_operator_with_names(self):
        """Test 'is' operator with variable names"""
        # Note: Names (identifiers) will be compared as strings, not identity
        assert Conditional.test('test is test') is True
        assert Conditional.test('apple is banana') is False

    def test_is_not_operator(self):
        """Test 'is not' operator"""
        assert Conditional.test('apple is not banana') is True
        assert Conditional.test('None is not None') is False

    def test_is_with_different_types(self):
        """Test 'is' with integers (note: small integers are cached in Python)"""
        # In Python, 1 is True returns False (different objects)
        assert Conditional.test('1 is True') is False  # Different ocjects
        assert Conditional.test('1 == True')


class TestConditionalEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_string_equality(self):
        """Test empty string comparisons"""
        assert Conditional.test('"" == ""') is True
        assert Conditional.test('"hello" == ""') is False

    def test_whitespace_in_strings(self):
        """Test strings with whitespace"""
        assert Conditional.test('"hello world" == "hello world"') is True
        assert Conditional.test('"hello" == "hello "') is False

    def test_special_characters_in_strings(self):
        """Test strings with special characters"""
        assert Conditional.test('"hello@world" == "hello@world"') is True
        assert Conditional.test('"a-b-c" == "a-b-c"') is True


class TestConditionalRealWorldScenarios:
    """Test real-world scenarios from the bug report"""

    def test_scenario_int_variable(self):
        """Test scenario with VAR_INT == '123'

        In the real system, after variable substitution:
        - $VAR_INT becomes the value "123"
        - The condition "$VAR_INT == 123" becomes "123 == 123" (both integers)
        - The condition '$VAR_INT == "123"' becomes '123 == "123"' (int vs string)
        """
        # After variable substitution, this becomes:
        assert Conditional.test('123 == "123"') is False  # Different types
        assert Conditional.test('123 == 123') is True     # Same type
        assert Conditional.test('"123" == "123"') is True  # Both strings

    def test_scenario_str_variable_no_crash(self):
        """Test scenario with VAR_STR == 'hello' - should NOT crash

        This is the main bug fix test. Before the fix, comparing a string
        variable to a string literal would crash with:
        ValueError: invalid literal for int() with base 10: 'hello'
        """
        # This should not crash anymore - the key test for the bug fix
        assert Conditional.test('hello == "hello"') is True
        assert Conditional.test('"hello" == hello') is True
        assert Conditional.test('"hello" == "hello"') is True

    def test_numeric_string_in_variable(self):
        """Test when a variable contains a numeric string"""
        # Variable contains "123" as a string
        assert Conditional.test('"123" == "123"') is True
        assert Conditional.test('"123" != 123') is True  # String vs int

    def test_original_crash_scenario(self):
        """Test the exact scenario that caused crash

        From demo_str.yml:
        only_if: $VAR_STR == "hello"

        After substitution becomes: hello == "hello"
        This would crash with the old code that forced int() conversion
        """
        # This exact expression caused the crash
        try:
            result = Conditional.test('hello == "hello"')
            assert result is True
        except ValueError as e:
            pytest.fail(f'Should not raise ValueError: {e}')
