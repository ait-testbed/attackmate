from attackmate.schemas.config import Config


class TestMsfConfigMigration:
    def test_old_flat_format_migrated_to_default_key(self):
        data = {'msf_config': {'password': 'secret', 'server': '127.0.0.1'}}
        c = Config.model_validate(data)
        assert 'default' in c.msf_config
        assert c.msf_config['default'].server == '127.0.0.1'
        assert c.msf_config['default'].password == 'secret'

    def test_old_flat_format_preserves_all_fields(self):
        data = {
            'msf_config': {
                'password': 'pw',
                'ssl': False,
                'port': 55554,
                'server': '10.0.0.1',
                'uri': '/rpc/'}}
        c = Config.model_validate(data)
        cfg = c.msf_config['default']
        assert cfg.port == 55554
        assert cfg.ssl is False
        assert cfg.uri == '/rpc/'

    def test_new_named_format_single_entry(self):
        data = {'msf_config': {'myserver': {'password': 'secret', 'server': '10.0.0.1'}}}
        c = Config.model_validate(data)
        assert list(c.msf_config.keys()) == ['myserver']
        assert c.msf_config['myserver'].server == '10.0.0.1'

    def test_new_named_format_multiple_entries(self):
        data = {
            'msf_config': {
                'server1': {'password': 'pw1', 'server': '10.0.0.1'},
                'server2': {'password': 'pw2', 'server': '10.0.0.2'},
            }
        }
        c = Config.model_validate(data)
        assert set(c.msf_config.keys()) == {'server1', 'server2'}
        assert c.msf_config['server1'].server == '10.0.0.1'
        assert c.msf_config['server2'].server == '10.0.0.2'

    def test_empty_msf_config_stays_empty(self):
        c = Config()
        assert c.msf_config == {}

    def test_named_entries_preserve_insertion_order(self):
        data = {
            'msf_config': {
                'primary': {'server': '10.0.0.1'},
                'secondary': {'server': '10.0.0.2'},
            }
        }
        c = Config.model_validate(data)
        assert next(iter(c.msf_config)) == 'primary'


class TestSliverConfigMigration:
    def test_old_flat_format_migrated_to_default_key(self):
        data = {'sliver_config': {'config_file': '/home/user/.sliver/config.cfg'}}
        c = Config.model_validate(data)
        assert 'default' in c.sliver_config
        assert c.sliver_config['default'].config_file == '/home/user/.sliver/config.cfg'

    def test_old_flat_format_with_none_config_file(self):
        data = {'sliver_config': {'config_file': None}}
        c = Config.model_validate(data)
        assert 'default' in c.sliver_config
        assert c.sliver_config['default'].config_file is None

    def test_new_named_format_single_entry(self):
        data = {'sliver_config': {'primary': {'config_file': '/path/to/cfg.cfg'}}}
        c = Config.model_validate(data)
        assert list(c.sliver_config.keys()) == ['primary']
        assert c.sliver_config['primary'].config_file == '/path/to/cfg.cfg'

    def test_new_named_format_multiple_entries(self):
        data = {
            'sliver_config': {
                'sliver1': {'config_file': '/path/cfg1.cfg'},
                'sliver2': {'config_file': '/path/cfg2.cfg'},
            }
        }
        c = Config.model_validate(data)
        assert set(c.sliver_config.keys()) == {'sliver1', 'sliver2'}
        assert c.sliver_config['sliver1'].config_file == '/path/cfg1.cfg'
        assert c.sliver_config['sliver2'].config_file == '/path/cfg2.cfg'

    def test_empty_sliver_config_stays_empty(self):
        c = Config()
        assert c.sliver_config == {}

    def test_named_entries_preserve_insertion_order(self):
        data = {
            'sliver_config': {
                'first': {'config_file': '/path/a.cfg'},
                'second': {'config_file': '/path/b.cfg'},
            }
        }
        c = Config.model_validate(data)
        assert next(iter(c.sliver_config)) == 'first'
