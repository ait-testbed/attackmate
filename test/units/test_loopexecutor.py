import logging
from attackmate.schemas.playbook import Commands
from attackmate.schemas.debug import DebugCommand
from attackmate.schemas.loop import LoopCommand
from attackmate.executors.common.debugexecutor import DebugExecutor
from attackmate.executors.common.loopexecutor import LoopExecutor
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


class TestLoopExecutor:
    def setup_method(self, method):
        self.varstore = VariableStore()
        self.process_manager = ProcessManager()
        self.debug_executor = DebugExecutor(self.process_manager, self.varstore)
        self.loop_executor = LoopExecutor(self.process_manager, varstore=self.varstore, runfunc=self.run_func)

    def run_func(self, commands: Commands):
        for command in commands:
            if command.type == 'debug':
                self.debug_executor.run(command)

    def test_items(self, caplog):
        caplog.set_level(logging.INFO)
        self.varstore.clear()
        self.varstore.set_variable('one', ['first', 'second'])
        lc = LoopCommand(type='loop',
                         cmd='items($one)',
                         commands=[DebugCommand(cmd='$LOOP_ITEM', type='debug')])
        self.loop_executor.run(lc)
        assert 'Debug: \'first\'' in [rec.message for rec in caplog.records]
        assert 'Debug: \'second\'' in [rec.message for rec in caplog.records]

    def test_range(self, caplog):
        caplog.set_level(logging.INFO)
        self.varstore.clear()
        self.varstore.set_variable('one', ['first', 'second'])
        lc = LoopCommand(type='loop',
                         cmd='range(1,3)',
                         commands=[DebugCommand(cmd='$LOOP_INDEX', type='debug')])
        self.loop_executor.run(lc)
        assert 'Debug: \'1\'' in [rec.message for rec in caplog.records]
        assert 'Debug: \'2\'' in [rec.message for rec in caplog.records]
