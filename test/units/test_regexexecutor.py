from unittest.mock import MagicMock
from attackmate.variablestore import VariableStore
from attackmate.processmanager import ProcessManager
from attackmate.schemas.regex import RegExCommand
from attackmate.executors.common.regexexecutor import RegExExecutor


class TestRegExExecutor:
    def setup_method(self, method):
        self.varstore = VariableStore()
        self.process_manager = ProcessManager()
        self.executor = RegExExecutor(self.process_manager, self.varstore)
        self.executor.logger = MagicMock()

    def test_log_command(self):
        command = RegExCommand(type='regex', cmd='test', mode='findall', output={})
        self.executor.log_command(command)
        self.executor.logger.warning.assert_called_once_with("RegEx: 'test', Mode: 'findall'")

    def test_forge_variables(self):

        # Test with None
        result = self.executor.forge_variables(None)
        assert result is None

        # Test with string
        result = self.executor.forge_variables('test')
        assert result == {'MATCH_0': 'test'}

        # Test with list of strings
        result = self.executor.forge_variables(['test1', 'test2'])
        assert result == {'MATCH_0': 'test1', 'MATCH_1': 'test2'}

        # Test with nested list
        result = self.executor.forge_variables([['test1', 'test2'], ['test3', 'test4']])
        assert result == {
            'MATCH_0_0': 'test1',
            'MATCH_0_1': 'test2',
            'MATCH_1_0': 'test3',
            'MATCH_1_1': 'test4',
        }

    def test_register_outputvars(self):
        matches = {'MATCH_0': 'test'}
        outputvars = {'output_var': 'Matched: $MATCH_0'}
        self.executor.register_outputvars(outputvars, matches)
        assert self.varstore.get_variable('output_var') == 'Matched: test'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['test']

    def test_forge_and_register_variables(self):
        output = {'output_var': 'Matched: $MATCH_0'}
        data = 'test'
        self.executor.forge_and_register_variables(output, data)
        assert self.varstore.get_variable('output_var') == 'Matched: test'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['test']

    def test_exec_cmd_findall(self):
        # Test mode "findall"
        self.varstore.set_variable('input_var', 'test1 test2 test3')
        command = RegExCommand(
            type='regex',
            cmd='test\\d',
            mode='findall',
            input='input_var',
            output={'output_var': 'Found: $MATCH_0, $MATCH_1, $MATCH_2'},
        )
        self.executor._exec_cmd(command)
        assert self.varstore.get_variable('output_var') == 'Found: test1, test2, test3'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['test1', 'test2', 'test3']

    def test_exec_cmd_split(self):
        # Test mode "split"
        self.varstore.set_variable('input_var', 'test1 test2 test3')
        command = RegExCommand(
            type='regex',
            cmd='\\s',
            mode='split',
            input='input_var',
            output={'output_var': 'First: $MATCH_0, Second: $MATCH_1, Third: $MATCH_2'},
        )
        self.executor._exec_cmd(command)
        assert self.varstore.get_variable('output_var') == 'First: test1, Second: test2, Third: test3'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['test1', 'test2', 'test3']

    def test_exec_cmd_search(self):
        # Test mode "search"
        self.varstore.set_variable('input_var', 'test1 test2 test3')
        command = RegExCommand(
            type='regex',
            cmd='test\\d',
            mode='search',
            input='input_var',
            output={'output_var': 'Found: $MATCH_0'},
        )
        self.executor._exec_cmd(command)
        assert self.varstore.get_variable('output_var') == 'Found: test1'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['test1']

    def test_exec_cmd_sub(self):
        # Test mode "sub"
        # emulates behaviour of re.sub, if no match is found input string is returned
        self.varstore.set_variable('input_var', 'test1 test2 test3')
        command = RegExCommand(
            type='regex',
            cmd='test',
            mode='sub',
            replace='TEST',
            input='input_var',
            output={'output_var': 'Replaced: $MATCH_0'},
        )
        self.executor._exec_cmd(command)
        assert self.varstore.get_variable('output_var') == 'Replaced: TEST1 TEST2 TEST3'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['TEST1 TEST2 TEST3']

    def test_exec_cmd_findall_no_match(self):
        # Test mode "findall" without matches
        self.varstore.set_variable('input_var', 'no matches here')
        command = RegExCommand(
            type='regex',
            cmd='test\\d',
            mode='findall',
            input='input_var',
            output={'output_var': 'Found: $MATCH_0'},
        )
        self.executor._exec_cmd(command)
        assert 'output_var' not in self.varstore.variables
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == []

    def test_exec_cmd_split_no_match(self):
        # Test mode "split" without matches
        # emulates behaviour of re.split, if no match is found input string is returned
        self.varstore.set_variable('input_var', 'no matches here')
        command = RegExCommand(
            type='regex', cmd='\\d', mode='split', input='input_var', output={'output_var': 'First: $MATCH_0'}
        )
        self.executor._exec_cmd(command)
        assert self.varstore.get_variable('output_var') == 'First: no matches here'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['no matches here']

    def test_exec_cmd_search_no_match(self):
        # Test mode "search" without matches
        self.varstore.set_variable('input_var', 'no matches here')
        command = RegExCommand(
            type='regex',
            cmd='test\\d',
            mode='search',
            input='input_var',
            output={'output_var': 'Found: $MATCH_0'},
        )
        self.executor._exec_cmd(command)
        assert 'output_var' not in self.varstore.variables
        assert 'REGEX_MATCHES_LIST' not in self.varstore.variables

    def test_exec_cmd_sub_no_match(self):
        # Test mode "sub" without matches
        # emulates behaviour of re.sub, if no match is found input string is returned
        self.varstore.set_variable('input_var', 'no matches here')
        command = RegExCommand(
            type='regex',
            cmd='test',
            mode='sub',
            replace='TEST',
            input='input_var',
            output={'output_var': 'Replaced: $MATCH_0'},
        )
        self.executor._exec_cmd(command)
        assert self.varstore.get_variable('output_var') == 'Replaced: no matches here'
        assert self.varstore.get_variable('REGEX_MATCHES_LIST') == ['no matches here']
