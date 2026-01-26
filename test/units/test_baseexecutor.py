import pytest
from attackmate.executors.baseexecutor import BaseExecutor
from attackmate.execexception import ExecException
from attackmate.result import Result
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.schemas.base import BaseCommand
from attackmate.schemas.regex import RegExCommand
from attackmate.schemas.sliver import SliverSessionEXECCommand


class DummyCommand(BaseCommand):
    return_val: int = 0
    return_str: str = 'back'
    return_except: bool = False


class DummyExecutor(BaseExecutor):
    async def _exec_cmd(self, command: DummyCommand):
        if command.return_except:
            raise ExecException('Failed')
        return Result(command.return_str, command.return_val)


class TestBaseExecutor:
    def test_replace_variables_in_strings(self):
        varstore = VariableStore()
        varstore.set_variable('foo', 'bar')
        varstore.set_variable('wonder', 'woman')
        be = BaseExecutor(ProcessManager(), varstore)
        bc = BaseCommand(cmd='$foo hello', exit_on_error=False, loop_if_not='world $wonder')
        replaced = be.substitute_template_vars(bc)
        assert replaced.cmd == 'bar hello'
        # exit_on_error must not have changed!
        assert replaced.exit_on_error is False
        assert replaced.loop_if_not == 'world woman'
        # original command must not change!
        assert bc.cmd == '$foo hello'
        assert bc.exit_on_error is False
        assert bc.loop_if_not == 'world $wonder'

    def test_replace_variables_in_dicts(self):
        varstore = VariableStore()
        varstore.set_variable('foo', 'bar')
        varstore.set_variable('wonder', 'woman')
        be = BaseExecutor(ProcessManager(), varstore)
        rex = RegExCommand(type='regex', cmd='$foo.*', output={'foo$foo': '$foo'}, input='hello world')
        replaced = be.substitute_template_vars(rex)
        assert replaced.cmd == 'bar.*'
        assert replaced.output['foo$foo'] == 'bar'
        # input must not have changed!
        assert replaced.input == 'hello world'
        # original command must not change!
        assert rex.cmd == '$foo.*'
        assert rex.output['foo$foo'] == '$foo'
        # input must not have changed!
        assert rex.input == 'hello world'

    def test_replace_variables_in_lists(self):
        varstore = VariableStore()
        varstore.set_variable('foo', 'bar')
        varstore.set_variable('wonder', 'woman')
        be = BaseExecutor(ProcessManager(), varstore)
        sl = SliverSessionEXECCommand(
            type='sliver-session',
            cmd='execute',
            exe='hello $foo',
            output=False,
            session='$foo $woman',
            args=['woo $wonder', 'hoo $foo'],
        )
        replaced = be.substitute_template_vars(sl)
        assert replaced.cmd == 'execute'
        assert replaced.session == 'bar $woman'
        assert replaced.exe == 'hello bar'
        assert replaced.output is False
        assert replaced.args[0] == 'woo woman'
        assert replaced.args[1] == 'hoo bar'
        assert sl.cmd == 'execute'
        assert sl.session == '$foo $woman'
        assert sl.exe == 'hello $foo'
        assert sl.output is False
        assert sl.args[0] == 'woo $wonder'
        assert sl.args[1] == 'hoo $foo'

    def test_variable_to_int(self):
        varstore = VariableStore()
        be = BaseExecutor(ProcessManager(), varstore)
        assert be.variable_to_int('foo', '1') == 1
        with pytest.raises(ExecException):
            be.variable_to_int('foo', '$var')

    @pytest.mark.asyncio
    async def test_dummy__exec(self):
        varstore = VariableStore()
        executor = DummyExecutor(ProcessManager(), varstore)
        dc = DummyCommand(cmd='dummy')
        assert dc.return_str == 'back'

        assert dc.return_val == 0
        result = await executor._exec_cmd(dc)
        assert result.returncode == dc.return_val
        assert result.stdout == dc.return_str
        dc.return_except = True
        with pytest.raises(ExecException):
            await executor._exec_cmd(dc)

    @pytest.mark.asyncio
    async def test_dummy_set_variables(self):
        varstore = VariableStore()
        executor = DummyExecutor(ProcessManager(), varstore)
        dc = DummyCommand(cmd='dummy')
        await executor.exec(dc)
        assert varstore.get_variable('RESULT_STDOUT') == dc.return_str
        assert varstore.get_variable('RESULT_RETURNCODE') == str(dc.return_val)

    @pytest.mark.asyncio
    async def test_dummy_exit_on_error(self):
        varstore = VariableStore()
        executor = DummyExecutor(ProcessManager(), varstore)
        dc = DummyCommand(cmd='dummy')
        dc.error_if = '.*back.*'
        with pytest.raises(SystemExit):
            await executor.exec(dc)
        dc.error_if = None
        dc.error_if_not = 'forward'
        with pytest.raises(SystemExit):
            await executor.exec(dc)
        dc.error_if = None
        dc.error_if_not = 'forward'

    @pytest.mark.asyncio
    async def test_dummy_loop(self):
        varstore = VariableStore()
        executor = DummyExecutor(ProcessManager(), varstore)
        executor.run_count = 1
        dc = DummyCommand(cmd='dummy', loop_if='back')
        with pytest.raises(SystemExit):
            await executor.exec(dc)
        dc = DummyCommand(cmd='dummy', loop_if='forward')
        try:
            await executor.exec(dc)
        except SystemExit:
            pytest.fail('Unexpected Exit')
        dc = DummyCommand(cmd='dummy', loop_if_not='forward')
        with pytest.raises(SystemExit):
            await executor.exec(dc)
        dc = DummyCommand(cmd='dummy', loop_if_not='back')
        try:
            await executor.exec(dc)
        except SystemExit:
            pytest.fail('Unexpected Exit')
