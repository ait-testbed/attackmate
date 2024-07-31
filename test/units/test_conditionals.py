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
        assert Conditional.test('1 is True')
        assert Conditional.test('0 is True') is False

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
