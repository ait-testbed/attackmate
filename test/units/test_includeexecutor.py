import logging
import textwrap
import pytest
from attackmate.schemas.include import IncludeCommand
from attackmate.schemas.playbook import Commands
from attackmate.executors.common.debugexecutor import DebugExecutor
from attackmate.executors.common.includeexecutor import IncludeExecutor
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager


@pytest.fixture
def varstore():
    return VariableStore()


@pytest.fixture
def process_manager():
    return ProcessManager()


@pytest.fixture
def debug_executor(process_manager, varstore):
    return DebugExecutor(process_manager, varstore)


@pytest.fixture
def include_executor(process_manager, varstore, debug_executor):
    async def run_func(commands: Commands):
        for command in commands:
            if command.type == 'debug':
                await debug_executor.run(command)

    return IncludeExecutor(process_manager, varstore=varstore, runfunc=run_func)


@pytest.fixture
def caplog_setup(caplog):
    caplog.set_level(logging.INFO)
    return caplog


class TestIncludeExecutor:

    @pytest.mark.asyncio
    async def test_commands_are_executed(self, caplog_setup, tmp_path, include_executor):
        """Commands in the included file are actually executed."""
        caplog = caplog_setup
        include_file = tmp_path / 'sub.yml'
        include_file.write_text(textwrap.dedent("""\
            commands:
              - type: debug
                cmd: "hello from include"
        """))
        cmd = IncludeCommand(type='include', local_path=str(include_file))
        await include_executor.run(cmd)
        assert "Debug: 'hello from include'" in [rec.message for rec in caplog.records]

    @pytest.mark.asyncio
    async def test_multiple_commands_are_executed_in_order(self, caplog_setup, tmp_path, include_executor):
        """All commands in the included file run, in order."""
        caplog = caplog_setup
        include_file = tmp_path / 'sub.yml'
        include_file.write_text(textwrap.dedent("""\
            commands:
              - type: debug
                cmd: "first"
              - type: debug
                cmd: "second"
              - type: debug
                cmd: "third"
        """))
        cmd = IncludeCommand(type='include', local_path=str(include_file))
        await include_executor.run(cmd)
        messages = [rec.message for rec in caplog.records]
        assert "Debug: 'first'" in messages
        assert "Debug: 'second'" in messages
        assert "Debug: 'third'" in messages
        first_idx = messages.index("Debug: 'first'")
        second_idx = messages.index("Debug: 'second'")
        third_idx = messages.index("Debug: 'third'")
        assert first_idx < second_idx < third_idx

    @pytest.mark.asyncio
    async def test_variable_substitution_in_included_commands(
            self, caplog_setup, tmp_path, varstore, include_executor):
        """Variables set before the include are visible inside the included file."""
        caplog = caplog_setup
        varstore.set_variable('GREETING', 'hello')
        include_file = tmp_path / 'sub.yml'
        include_file.write_text(textwrap.dedent("""\
            commands:
              - type: debug
                cmd: "$GREETING world"
        """))
        cmd = IncludeCommand(type='include', local_path=str(include_file))
        await include_executor.run(cmd)
        assert "Debug: 'hello world'" in [rec.message for rec in caplog.records]

    @pytest.mark.asyncio
    async def test_missing_file_exits(self, tmp_path, include_executor):
        """A missing include file causes the executor to exit (exit_on_error behaviour)."""
        cmd = IncludeCommand(type='include', local_path=str(tmp_path / 'nonexistent.yml'))
        with pytest.raises(SystemExit):
            await include_executor.run(cmd)
