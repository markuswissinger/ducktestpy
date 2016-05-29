import os
import types
import unittest

from hamcrest import assert_that, is_
from mock import Mock

from ducktest import run
from ducktest.typer import Finding, TypeWrapper
from tests.sample import sample_findings


class TypeWrapperTest(unittest.TestCase):
    def test_other_type(self):
        assert TypeWrapper(1) != 1

    def test_equals(self):
        assert TypeWrapper(1) == TypeWrapper(1)

    def test_unequal_int(self):
        assert TypeWrapper(1) == TypeWrapper(2)

    def test_unequal_type(self):
        assert TypeWrapper(1) != TypeWrapper('1')

    def test_in_set(self):
        a = TypeWrapper(1)
        b = TypeWrapper(2)
        c = TypeWrapper(3)
        assert_that({a, b}, is_({c}))


class ConfigMock(object):
    def __init__(self, path):
        here = os.path.dirname(os.path.abspath(__file__))
        self.sample_dir = os.path.join(here, 'sample', path)
        self.top_level_directory = os.path.split(here)[0]
        self.discover_tests_in_directories = [self.sample_dir]
        self.write_docstrings_in_directories = [self.sample_dir]
        self.ignore_call_parameter_names = ['self', 'cls']
        self.ignore_classes = ['mock.Mock']

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

    def test_list(self):
        conf = ConfigMock('list')
        full_file = conf.in_sample_path('list.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.all_file_names(), is_([full_file]))

        findings = typing_debugger.get_sorted_findings(full_file)
        assert_that(findings, is_(sample_findings.single_type_list(full_file)))

    def test_imported_types(self):
        conf = ConfigMock('imported_types')
        full_file = conf.in_sample_path('imported_types.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.all_file_names(), is_([full_file]))

        findings = typing_debugger.get_sorted_findings(full_file)
        assert_that(findings, is_(sample_findings.imported_types(full_file)))

    def test_several_calls(self):
        conf = ConfigMock('several_calls')
        full_file = conf.in_sample_path('several_calls.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.all_file_names(), is_([full_file]))

        findings = typing_debugger.get_sorted_findings(full_file)
        assert_that(findings, is_(sample_findings.several_calls(full_file)))

    def test_autospec_call(self):
        conf = ConfigMock('autospec')
        full_file = conf.in_sample_path('autospec.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.all_file_names(), is_([full_file]))

        findings = typing_debugger.get_sorted_findings(full_file)
        assert_that(findings, is_(sample_findings.autospec_call(full_file)))

    def test_plain_mock(self):
        conf = ConfigMock('plain_mock')
        full_file = conf.in_sample_path('plain_mock.py')
        typing_debugger = run(conf)

        assert_that(typing_debugger.all_file_names(), is_([full_file]))

        findings = typing_debugger.get_sorted_findings(full_file)
        assert_that(findings, is_(sample_findings.plain_mock(full_file)))
