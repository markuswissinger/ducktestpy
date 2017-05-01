import os
import re
import unittest

from hamcrest import assert_that, is_
from mock import Mock

import ducktest
from ducktest.configuration import DucktestConfiguration
from ducktest.sphinx_docstring import DocstringWriter, read_file
from tests.matchers import is_same_list_of_lines

regex = re.compile('test_([^\.]*)')

PATH = os.path.dirname(os.path.dirname(__file__))


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.old_write = ducktest.sphinx_docstring.write_file
        self.write = Mock()
        ducktest.sphinx_docstring.write_file = self.write

    def tearDown(self):
        ducktest.sphinx_docstring.write_file = self.old_write

    def get_lines(self, file_name):
        for call in self.write.call_args_list:
            name, lines = call[0]
            if name == os.path.join(PATH, 'sample', file_name, 'original.py'):
                return lines

    def assert_sphinx_docstring_written_in_folder(self, name):
        directories = [('sample', name)]
        DucktestConfiguration(
            os.path.join(PATH, 'dummy.py'),
            test_directories=directories,
            write_directories=directories,
        ).run()

        received = self.get_lines(name)
        expected = read_file(os.path.join(PATH, 'sample', name, 'expected_sphinx.py'))

        assert_that(received, is_same_list_of_lines(expected))
        assert_that(len(received), is_(len(expected)))

    def test_dictionary(self):
        self.assert_sphinx_docstring_written_in_folder('dictionary')

    def test_supertypes(self):
        self.assert_sphinx_docstring_written_in_folder('supertypes')

    def test_raising(self):
        self.assert_sphinx_docstring_written_in_folder('raising')

    def test_module_constants(self):
        self.assert_sphinx_docstring_written_in_folder('module_constants')

    def test_string_in_docstring(self):
        self.assert_sphinx_docstring_written_in_folder('string_in_docstring')

    def test_integration(self):
        self.assert_sphinx_docstring_written_in_folder('integration')
