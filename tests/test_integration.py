import os
import unittest

from hamcrest import assert_that, is_
from mock import Mock

from ducktest import docstring_writer

from ducktest import run
from ducktest.typer import Finding


class ConfigMock(object):
    def __init__(self, path):
        here = os.path.dirname(os.path.abspath(__file__))
        self.sample_dir = os.path.join(here, 'sample', path)
        self.top_level_directory = os.path.split(here)[0]
        self.discover_tests_in_directories = [self.sample_dir]
        self.write_docstrings_in_directories = [self.sample_dir]
        self.ignore_call_parameter_names = ['self', 'cls']

    def in_sample_path(self, file_name):
        return os.path.join(self.sample_dir, file_name)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.old = docstring_writer.write_file
        self.written = Mock()
        docstring_writer.write_file = self.written

    def tearDown(self):
        docstring_writer.write_file = self.old

    def test_module_method(self):
        conf = ConfigMock('module_method')
        file_path = conf.in_sample_path('module_method.py')

        typing_debugger = run(conf)

        finding = Finding()
        finding.file_name = file_path
        finding.function_name = 'some_method'
        finding.first_line_number = 1
        finding.call_types.update({'a': {int}})
        finding.return_types.update({int})
        finding.docstring = None

        assert_that(typing_debugger.get_sorted_findings(file_path), is_([finding]))
        assert_that(typing_debugger.all_file_names(), is_([file_path]))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(conf.in_sample_path('module_method.py'), [
            'def some_method(a):\n',
            '    """\n',
            '    :type a: int\n',
            '    :rtype: int\n',
            '    """\n',
            '    return a\n',
        ])

    def test_method_in_class(self):
        conf = ConfigMock('method_in_class')
        typing_debugger = run(conf)

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(conf.in_sample_path('method_in_class.py'), [
            'class SomeClass(object):\n',
            '    def __init__(self, b):\n',
            '        """:type b: int"""\n',
            '        self.b = b\n',
            '\n',
            '    def some_method(self, a):\n',
            '        """\n',
            '        :type a: int\n',
            '        :rtype: int\n',
            '        """\n',
            '        return self.b + a\n',
        ])

    def test_generator(self):
        conf = ConfigMock('generator')
        typing_debugger = run(conf)

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(conf.in_sample_path('generator.py'), [
            'def some_generator():\n',
            '    """:rtype: generator"""\n',
            '    yield 1',
        ])

    def test_classmethod(self):
        conf = ConfigMock('classmethod')
        typing_debugger = run(conf)

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(conf.in_sample_path('classmethod.py'), [
            'class AnotherClass(object):\n',
            '    b = 1\n',
            '\n',
            '    @classmethod\n',
            '    def some_classmethod(cls, a):\n',
            '        """\n',
            '        :type a: int\n',
            '        :rtype: int\n',
            '        """\n',
            '        return a + cls.b\n',
        ])
