import os
import unittest

from hamcrest import assert_that, is_
from mock import Mock

import ducktest
from ducktest.configuration import DucktestConfiguration
from ducktest.sphinx_docstring import DocstringWriter, read_file


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.old_write = ducktest.sphinx_docstring.write_file
        self.write = Mock()
        ducktest.sphinx_docstring.write_file = self.write

        self.path = os.path.dirname(__file__)

    def get_lines(self):
        for call in self.write.call_args_list:
            name, lines = call[0]
            if name == os.path.join(self.path, 'sample', 'integration', 'integration.py'):
                return lines

    def test_integration(self):
        DucktestConfiguration(
            self.path,
            test_directories=['tests/sample/integration'.split('/')],
            write_directories=['tests/sample/integration'.split('/')],
        ).run()

        lines = self.get_lines()

        expected = read_file(os.path.join(self.path, 'sample', 'integration', 'expectation.py'))

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
        ducktest.sphinx_docstring.write_file = self.old_write
