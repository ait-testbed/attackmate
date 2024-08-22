from attackmate.variablestore import VariableStore


class TestVariableStore:

    def test_set_and_get_variable(self):
        var_store = VariableStore()
        old_len = len(var_store.variables)
        var_store.set_variable('foo', 'bar')
        assert len(var_store.variables) == old_len + 1
        assert var_store.get_variable('foo') == 'bar'

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

    def test_remove_sign(self):
        var_store = VariableStore()
        assert var_store.remove_sign('$foo', '$') == 'foo'
        assert var_store.remove_sign('$$foo', '$') == '$foo'
        assert var_store.remove_sign('@foo', '$') == '@foo'

    def test_from_dict(self):
        var_store = VariableStore()
        var_store.set_variable('hello', 'world')
        var_blah = {'a': 'foo', 'b': 'bar'}
        var_store.from_dict(var_blah)
        assert var_store.get_variable('hello') == 'world'
        assert var_store.get_variable('a') == 'foo'
        assert var_store.get_variable('b') == 'bar'
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
