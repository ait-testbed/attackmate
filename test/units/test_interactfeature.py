import time
from attackmate.executors.ssh.interactfeature import Interactive


class TestCheckPrompt:
    def setup_method(self):
        self.interactive = Interactive()
        self.interactive.set_timer()

    def test_no_prompts_configured_resets_timer(self):
        before = self.interactive.timer
        time.sleep(0.05)
        self.interactive.check_prompt('some output', [])
        assert self.interactive.timer > before

    def test_prompt_not_matched_resets_timer(self):
        before = self.interactive.timer
        time.sleep(0.05)
        result = self.interactive.check_prompt('still running...', ['$ '])
        assert result is False
        assert self.interactive.timer > before

    def test_prompt_matched_clears_timer_and_returns_true(self):
        result = self.interactive.check_prompt('root@host:~$ ', ['$ '])
        assert result is True
        assert self.interactive.timer is None

    def test_empty_output_on_channel_eof_does_not_reset_timer(self):
        before = self.interactive.timer
        time.sleep(0.05)
        result = self.interactive.check_prompt('', ['$ '])
        assert result is False
        assert self.interactive.timer == before
