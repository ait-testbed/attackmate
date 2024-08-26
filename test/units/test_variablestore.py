from attackmate.variablestore import VariableNotFound, VariableStore, ListParseException
import unittest


class TestVariableStore(unittest.TestCase):

    def test_set_and_get_variable(self):
        var_store = VariableStore()
        old_len = len(var_store.variables)
        var_store.set_variable('foo', 'bar')
        assert len(var_store.variables) == old_len + 1
        assert var_store.get_variable('foo') == 'bar'
        var_store.set_variable('hello', ['world', 'mundo'])
        assert len(var_store.get_variable('hello')) == 2
        assert var_store.get_variable('hello')[0] == 'world'
        assert var_store.get_variable('hello')[1] == 'mundo'
        var_store.set_variable('hello[1]', 'lala')
        assert var_store.get_variable('hello')[1] == 'lala'
        tmp = 'hello'
        var_store.set_variable('hello[1]', tmp)
        tmp = 'yolo'
        assert var_store.get_variable('hello')[1] == 'hello'
        self.assertRaises(VariableNotFound, var_store.get_variable, 'notfound')

    def test_substitute_variable(self):
        var_store = VariableStore()
        var_store.set_variable('foo', 'bar')
        assert var_store.substitute('hello foo $foo') == 'hello foo bar'
        assert var_store.substitute('hello foo $foo', True) == 'hello foo bar'
        assert var_store.substitute('hello foo $bar') == 'hello foo $bar'
        assert var_store.substitute('hello foo $$foo') == 'hello foo $foo'
        assert var_store.substitute('hello foo $bar', True) == ''
        assert var_store.substitute(None) is None
        assert var_store.substitute(None, True) is None
        assert var_store.substitute(list['a', 'b']) == list['a', 'b']
        var_store.set_variable('first', ['one', 'two'])
        assert var_store.substitute('hello $first[0] $foo') == 'hello one bar'
        assert var_store.substitute('hello $first[1] $foo') == 'hello two bar'

    def test_remove_sign(self):
        var_store = VariableStore()
        assert var_store.remove_sign('$foo', '$') == 'foo'
        assert var_store.remove_sign('$$foo', '$') == '$foo'
        assert var_store.remove_sign('@foo', '$') == '@foo'

    def test_from_dict(self):
        var_store = VariableStore()
        var_store.set_variable('hello', 'world')
        var_blah = {'a': 'foo', 'b': 'bar', 'lista': ['one', 'two']}
        var_store.from_dict(var_blah)
        assert var_store.get_variable('hello') == 'world'
        assert var_store.get_variable('a') == 'foo'
        assert var_store.get_variable('b') == 'bar'
        assert var_store.get_variable('lista')[0] == 'one'
        assert var_store.get_variable('lista')[1] == 'two'
        assert len(var_store.variables) == 3
        var_store.from_dict(['a'])
        assert len(var_store.variables) == 3
        var_store.from_dict(None)
        assert len(var_store.variables) == 3

    def test_clear(self):
        var_store = VariableStore()
        var_store.set_variable('hello', 'world')
        assert len(var_store.variables) == 1
        var_store.clear()
        assert len(var_store.variables) == 0

    def test_is_list(self):
        assert VariableStore.is_list('blah') is False
        assert VariableStore.is_list('blah][') is False
        assert VariableStore.is_list('blah]') is False
        assert VariableStore.is_list('blah[]') is False
        assert VariableStore.is_list('blah["one"]') is False
        assert VariableStore.is_list('blah[1]') is True
        assert VariableStore.is_list('$blah[1]') is True

    def test_parse_list(self):
        result = VariableStore.parse_list('$blah[0]')
        assert result[0] == '$blah'
        assert result[1] == 0
        self.assertRaises(ListParseException, VariableStore.parse_list, 'blah["hello]')
        self.assertRaises(ListParseException, VariableStore.parse_list, 'blah[\'hello]')
        self.assertRaises(ListParseException, VariableStore.parse_list, 'blah[hello"]')
        self.assertRaises(ListParseException, VariableStore.parse_list, 'blah[hello\']')
        self.assertRaises(ListParseException, VariableStore.parse_list, 'blah[\'hello"]')
        self.assertRaises(ListParseException, VariableStore.parse_list, 'blah["hello\']')
        self.assertRaises(ListParseException, VariableStore.parse_list, 'blah[]')

    def test_get_list_variables(self) -> None:
        var_store: VariableStore = VariableStore()
        var_store.set_variable('first', ['a', 'b', 'c'])
        var_store.set_variable('second', ['one', 'two', 'three'])
        all_list_vars = var_store.get_lists_variables()
        assert all_list_vars['first[0]'] == 'a'
        assert all_list_vars['first[1]'] == 'b'
        assert all_list_vars['first[2]'] == 'c'
        assert all_list_vars['second[0]'] == 'one'
        assert all_list_vars['second[1]'] == 'two'
        assert all_list_vars['second[2]'] == 'three'
