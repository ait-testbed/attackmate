import time
from attackmate.attackmate import AttackMate
from attackmate.schemas.config import Config, CommandConfig
from attackmate.schemas.playbook import Playbook
from attackmate.schemas.debug import DebugCommand
from attackmate.schemas.setvar import SetVarCommand
from attackmate.schemas.shell import ShellCommand
from attackmate.schemas.sleep import SleepCommand


def test_command_delay_is_applied():
    """
    Tests that command_delay is applied between applicable commands.
    """
    delay = 0.2
    num_commands = 3
    playbook = Playbook(
        commands=[
            ShellCommand(type='shell', cmd='echo 1'),
            ShellCommand(type='shell', cmd='echo 2'),
            ShellCommand(type='shell', cmd='echo 3'),
        ]
    )
    config = Config(cmd_config=CommandConfig(command_delay=delay))
    attackmate_instance = AttackMate(playbook=playbook, config=config)

    start_time = time.monotonic()
    attackmate_instance._run_commands(attackmate_instance.playbook.commands)
    end_time = time.monotonic()
    elapsed_time = end_time - start_time

    expected_minimum_time = num_commands * delay
    # Allow for command execution overhead
    expected_maximum_time = expected_minimum_time + 0.5

    assert elapsed_time >= expected_minimum_time, (
        f'Execution faster ({elapsed_time:.4f}s) than the minimum expected delay '
        f'({expected_minimum_time:.4f}s).'
    )
    assert elapsed_time < expected_maximum_time, (
        f'Execution slower ({elapsed_time:.4f}s) than expected.'
    )


def test_zero_command_delay():
    """
    Tests that no delay is applied when command_delay is 0.
    """
    playbook = Playbook(
        commands=[
            ShellCommand(type='shell', cmd='echo 1'),
            ShellCommand(type='shell', cmd='echo 2'),
        ]
    )
    config = Config(cmd_config=CommandConfig(command_delay=0))
    attackmate_instance = AttackMate(playbook=playbook, config=config)

    start_time = time.monotonic()
    attackmate_instance._run_commands(attackmate_instance.playbook.commands)
    end_time = time.monotonic()
    elapsed_time = end_time - start_time

    # With no delay, execution should be very fast.
    assert elapsed_time < 0.1, (
        f'Execution with no delay took too long: {elapsed_time:.4f}s.'
    )


def test_delay_is_not_applied_for_exempt_commands():
    """
    Tests that delay is skipped for 'sleep', 'debug', and 'setvar' commands.
    """
    playbook = Playbook(
        commands=[
            SetVarCommand(type='setvar', cmd='x', variable='y'),
            DebugCommand(type='debug', cmd='test message'),
            SleepCommand(type='sleep', seconds=0),
        ]
    )
    # This delay should be ignored
    config = Config(cmd_config=CommandConfig(command_delay=5))
    attackmate_instance = AttackMate(playbook=playbook, config=config)

    start_time = time.monotonic()
    attackmate_instance._run_commands(attackmate_instance.playbook.commands)
    end_time = time.monotonic()
    elapsed_time = end_time - start_time

    assert elapsed_time < 0.1, (
        f'Execution with exempt commands took too long: {elapsed_time:.4f}s.'
    )
