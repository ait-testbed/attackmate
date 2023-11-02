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
