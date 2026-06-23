import time
from unittest.mock import patch
import pytest
from attackmate.attackmate import AttackMate
from attackmate.schemas.config import Config, CommandConfig
from attackmate.schemas.playbook import Playbook
from attackmate.schemas.debug import DebugCommand
from attackmate.schemas.setvar import SetVarCommand
from attackmate.schemas.shell import ShellCommand
from attackmate.schemas.sleep import SleepCommand


@pytest.mark.asyncio
async def test_command_delay_is_applied():
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
    await attackmate_instance._run_commands(attackmate_instance.playbook.commands)
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


@pytest.mark.asyncio
async def test_zero_command_delay():
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
    await attackmate_instance._run_commands(attackmate_instance.playbook.commands)
    end_time = time.monotonic()
    elapsed_time = end_time - start_time

    # With no delay, execution should be very fast.
    assert elapsed_time < 0.1, (
        f'Execution with no delay took too long: {elapsed_time:.4f}s.'
    )


@pytest.mark.asyncio
async def test_delay_is_not_applied_for_exempt_commands():
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
    await attackmate_instance._run_commands(attackmate_instance.playbook.commands)
    end_time = time.monotonic()
    elapsed_time = end_time - start_time

    assert elapsed_time < 0.1, (
        f'Execution with exempt commands took too long: {elapsed_time:.4f}s.'
    )


@pytest.mark.asyncio
async def test_jitter_off_behavior_unchanged():
    """
    With jitter disabled (default), behavior is identical to fixed command_delay.
    """
    delay = 0.1
    playbook = Playbook(commands=[ShellCommand(type='shell', cmd='echo 1')])
    config = Config(cmd_config=CommandConfig(command_delay=delay, command_delay_jitter=False))
    attackmate_instance = AttackMate(playbook=playbook, config=config)

    with patch('attackmate.attackmate.time.sleep') as mock_sleep:
        await attackmate_instance._run_commands(attackmate_instance.playbook.commands)
        mock_sleep.assert_called_once_with(delay)


@pytest.mark.asyncio
async def test_jitter_on_computes_correct_delay():
    """
    With jitter enabled, actual delay = command_delay + sign * uniform(jitter_min, jitter_max),
    clamped to >= 0.
    """
    playbook = Playbook(commands=[ShellCommand(type='shell', cmd='echo 1')])
    config = Config(cmd_config=CommandConfig(
        command_delay=1.0,
        command_delay_jitter=True,
        command_delay_jitter_min=0.5,
        command_delay_jitter_max=2.0,
    ))
    attackmate_instance = AttackMate(playbook=playbook, config=config)

    with patch('attackmate.attackmate.random.uniform', return_value=0.8) as mock_uniform, \
            patch('attackmate.attackmate.random.choice', return_value=1) as mock_choice, \
            patch('attackmate.attackmate.time.sleep') as mock_sleep:
        await attackmate_instance._run_commands(attackmate_instance.playbook.commands)
        mock_uniform.assert_called_once_with(0.5, 2.0)
        mock_choice.assert_called_once_with([-1, 1])
        # 1.0 + 1 * 0.8 = 1.8, clamped to >= 0 → 1.8
        mock_sleep.assert_called_once_with(1.8)


@pytest.mark.asyncio
async def test_jitter_clamped_to_zero():
    """
    When jitter produces a negative effective delay, it is clamped to 0.
    """
    playbook = Playbook(commands=[ShellCommand(type='shell', cmd='echo 1')])
    config = Config(cmd_config=CommandConfig(
        command_delay=0.0,
        command_delay_jitter=True,
        command_delay_jitter_min=0.5,
        command_delay_jitter_max=2.0,
    ))
    attackmate_instance = AttackMate(playbook=playbook, config=config)

    with patch('attackmate.attackmate.random.uniform', return_value=1.5), \
            patch('attackmate.attackmate.random.choice', return_value=-1), \
            patch('attackmate.attackmate.time.sleep') as mock_sleep:
        await attackmate_instance._run_commands(attackmate_instance.playbook.commands)
        # 0.0 + (-1) * 1.5 = -1.5, clamped → 0.0
        mock_sleep.assert_called_once_with(0.0)
