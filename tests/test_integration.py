import unittest

from hamcrest import assert_that, is_
from mock import Mock

import ducktest

from ducktest.type_wrappers import run
from ducktest.docstring_parser import DocstringWriter, read_file


class ConfigMock(object):
    def __init__(self):
        self.top_level_directory = '/home/markus/git/ducktestpy'
        self.discover_tests_in_directories = ['/home/markus/git/ducktestpy/tests/sample/integration']
        self.write_docstrings_in_directories = ['/home/markus/git/ducktestpy/tests/sample/integration']
        self.ignore_call_parameter_names = ['self', 'cls']


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.old_write = ducktest.docstring_parser.write_file
        self.write = Mock()
        ducktest.docstring_parser.write_file = self.write

    def get_lines(self):
        for call in self.write.call_args_list:
            name, lines = call[0]
            if name == '/home/markus/git/ducktestpy/tests/sample/integration/integration.py':
                return lines

    def test_integration(self):
        config_mock = ConfigMock()
        typing_debugger, processors = run(config_mock)

        DocstringWriter(processors, config_mock.write_docstrings_in_directories).write_all()

        lines = self.get_lines()

        expected = read_file('/home/markus/git/ducktestpy/tests/sample/integration/expectation.py')

        assert_that(lines, is_(expected))

        i = 1
        for line, expected_line in zip(lines, expected):
            i += 1
            try:
                assert_that(line, is_(expected_line))
            except AssertionError as e:
                print('Error in line {}'.format(i))
                raise e

    def tearDown(self):
        ducktest.docstring_parser.write_file = self.old_write
