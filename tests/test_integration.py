import os
import unittest

from mock import Mock

from ducktest import docstring_writer

from ducktest import run


class ConfigMock(object):
    here = os.path.dirname(os.path.abspath(__file__))
    sample_dir = os.path.join(here, 'sample')
    top_level_directory = os.path.split(here)[0]
    discover_tests_in_directories = [sample_dir]
    write_docstrings_in_directories = [sample_dir]
    ignore_call_parameter_names = ['self', 'cls']

    @classmethod
    def in_sample(cls, file_name):
        return os.path.join(cls.sample_dir, file_name)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.old = docstring_writer.write_file
        self.written = Mock()
        docstring_writer.write_file = self.written

    def tearDown(self):
        docstring_writer.write_file = self.old

    def test_sample(self):
        run(ConfigMock)
        self.written.assert_called_with(ConfigMock.in_sample('module_method.py'), [
            'def some_method(a):\n',
            '    """\n',
            '    :type a: int\n',
            '    :rtype: int\n',
            '    """\n',
            '    return a\n',
        ])
