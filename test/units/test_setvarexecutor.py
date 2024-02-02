from attackmate.variablestore import VariableStore
from attackmate.executors.common.setvarexecutor import SetVarExecutor
from attackmate.schemas.setvar import SetVarCommand
from attackmate.processmanager import ProcessManager


class TestSetVarExecutor:
    def test_set_variable(self):
        varstore = VariableStore()
        varstore.set_variable('PREFIX', 'new')
        executor = SetVarExecutor(ProcessManager(), varstore)
        command = SetVarCommand(cmd='Hello $PREFIX World', variable='Greeting', type='setvar')
        executor.run(command)
        assert varstore.get_variable('Greeting') == 'Hello new World'
