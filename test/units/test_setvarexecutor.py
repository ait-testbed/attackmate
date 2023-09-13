from attackmate.variablestore import VariableStore
from attackmate.setvarexecutor import SetVarExecutor
from attackmate.schemas import SetVarCommand


class TestSetVarExecutor:
    def test_set_variable(self):
        varstore = VariableStore()
        varstore.set_variable("PREFIX", "new")
        executor = SetVarExecutor(varstore)
        command = SetVarCommand(cmd="Hello $PREFIX World", variable="Greeting", type="setvar")
        executor.run(command)
        assert varstore.get_variable("Greeting") == "Hello new World"
