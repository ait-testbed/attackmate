from attackmate.baseexecutor import BaseExecutor
from attackmate.variablestore import VariableStore
from attackmate.schemas import BaseCommand, RegExCommand, SliverSessionEXECCommand


class TestBaseExecutor:

    def test_replace_variables_in_strings(self):
        varstore = VariableStore()
        varstore.set_variable("foo", "bar")
        varstore.set_variable("wonder", "woman")
        be = BaseExecutor(varstore)
        bc = BaseCommand(cmd="$foo hello", exit_on_error=False, loop_if_not="world $wonder")
        replaced = be.replace_variables(bc)
        assert replaced.cmd == "bar hello"
        # exit_on_error must not have changed!
        assert replaced.exit_on_error is False
        assert replaced.loop_if_not == "world woman"
        # original command must not change!
        assert bc.cmd == "$foo hello"
        assert bc.exit_on_error is False
        assert bc.loop_if_not == "world $wonder"

    def test_replace_variables_in_dicts(self):
        varstore = VariableStore()
        varstore.set_variable("foo", "bar")
        varstore.set_variable("wonder", "woman")
        be = BaseExecutor(varstore)
        rex = RegExCommand(type="regex", cmd="$foo.*", output={"foo$foo": "$foo"}, input="hello world")
        replaced = be.replace_variables(rex)
        assert replaced.cmd == "bar.*"
        assert replaced.output["foo$foo"] == "bar"
        # input must not have changed!
        assert replaced.input == "hello world"
        # original command must not change!
        assert rex.cmd == "$foo.*"
        assert rex.output["foo$foo"] == "$foo"
        # input must not have changed!
        assert rex.input == "hello world"

    def test_replace_variables_in_lists(self):
        varstore = VariableStore()
        varstore.set_variable("foo", "bar")
        varstore.set_variable("wonder", "woman")
        be = BaseExecutor(varstore)
        sl = SliverSessionEXECCommand(type="sliver-session", cmd="execute",
                                      exe="hello $foo", output=False, session="$foo $woman",
                                      args=["woo $wonder", "hoo $foo"])
        replaced = be.replace_variables(sl)
        assert replaced.cmd == "execute"
        assert replaced.session == "bar $woman"
        assert replaced.exe == "hello bar"
        assert replaced.output is False
        assert replaced.args[0] == "woo woman"
        assert replaced.args[1] == "hoo bar"
        assert sl.cmd == "execute"
        assert sl.session == "$foo $woman"
        assert sl.exe == "hello $foo"
        assert sl.output is False
        assert sl.args[0] == "woo $wonder"
        assert sl.args[1] == "hoo $foo"
