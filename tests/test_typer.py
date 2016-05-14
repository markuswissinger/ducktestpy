import os
import types
import unittest

from hamcrest import assert_that, is_

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


class TestTypeCollection(unittest.TestCase):
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

    def test_method_in_class(self):
        conf = ConfigMock('method_in_class')
        file_path = conf.in_sample_path('method_in_class.py')
        typing_debugger = run(conf)

        finding_5 = Finding()
        finding_5.file_name = file_path
        finding_5.function_name = 'some_method'
        finding_5.first_line_number = 5
        finding_5.call_types.update({'a': {int}})
        finding_5.return_types.update({int})
        finding_5.docstring = None

        finding_2 = Finding()
        finding_2.file_name = file_path
        finding_2.function_name = '__init__'
        finding_2.first_line_number = 2
        finding_2.call_types.update({'b': {int}})
        finding_2.docstring = None

        assert_that(typing_debugger.get_sorted_findings(file_path), is_([finding_5, finding_2]))
        assert_that(typing_debugger.all_file_names(), is_([file_path]))

    def test_generator(self):
        conf = ConfigMock('generator')
        file_path = conf.in_sample_path('generator.py')
        typing_debugger = run(conf)

        finding = Finding()
        finding.file_name = file_path
        finding.function_name = 'some_generator'
        finding.first_line_number = 1
        finding.return_types.update({types.GeneratorType})
        finding.docstring = None

        assert_that(typing_debugger.get_sorted_findings(file_path), is_([finding]))
        assert_that(typing_debugger.all_file_names(), is_([file_path]))

    def test_classmethod(self):
        conf = ConfigMock('classmethod')
        file_path = conf.in_sample_path('classmethod.py')
        typing_debugger = run(conf)

        finding = Finding()
        finding.file_name = file_path
        finding.function_name = 'some_classmethod'
        finding.first_line_number = 4
        finding.call_types.update({'a': {int}})
        finding.return_types.update({int})
        finding.docstring = None

        assert_that(typing_debugger.get_sorted_findings(file_path), is_([finding]))
        assert_that(typing_debugger.all_file_names(), is_([file_path]))
