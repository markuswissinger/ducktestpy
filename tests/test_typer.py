import os
import types
import unittest

from hamcrest import assert_that, is_

from ducktest import run
from ducktest.typer import Finding, TypeWrapper
from tests.sample import sample_findings


class TypeWrapperTest(unittest.TestCase):
    def test_equals(self):
        assert TypeWrapper(1) == TypeWrapper(1)

    def test_unequal(self):
        assert TypeWrapper(1) != TypeWrapper(2)


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
        full_file = conf.in_sample_path('module_method.py')

        typing_debugger = run(conf)

        assert_that(typing_debugger.get_sorted_findings(full_file), is_(sample_findings.module_method(full_file)))
        assert_that(typing_debugger.all_file_names(), is_([full_file]))

    def test_method_in_class(self):
        conf = ConfigMock('method_in_class')
        full_file = conf.in_sample_path('method_in_class.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.get_sorted_findings(full_file), is_(sample_findings.method_in_class(full_file)))
        assert_that(typing_debugger.all_file_names(), is_([full_file]))

    def test_generator(self):
        conf = ConfigMock('generator')
        full_file = conf.in_sample_path('generator.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.get_sorted_findings(full_file), is_(sample_findings.generator(full_file)))
        assert_that(typing_debugger.all_file_names(), is_([full_file]))

    def test_classmethod(self):
        conf = ConfigMock('classmethod')
        full_file = conf.in_sample_path('classmethod.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.all_file_names(), is_([full_file]))

        findings = typing_debugger.get_sorted_findings(full_file)
        assert_that(findings, is_(sample_findings.class_method(full_file)))