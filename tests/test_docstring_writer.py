"""
Copyright 2016 Markus Wissinger. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import unittest

from hamcrest import assert_that, is_

from mock import Mock

from ducktest import docstring_writer
from ducktest.docstring_writer import docstring_positions, DocstringTypeWrapper
from ducktest.typer import TypeWrapper
from tests.sample import sample_findings
from tests.sample.imported_types.to_import import ToImportA


class TestDocstringTypeWrapper(unittest.TestCase):
    def test_module_name(self):
        wrapper = TypeWrapper(ToImportA())
        assert_that(str(DocstringTypeWrapper(wrapper)), is_('tests.sample.imported_types.to_import.ToImportA'))


class TestDocstringPositionParser(unittest.TestCase):
    def test_parse_class(self):
        some_file = [
            'class Some(object):\n',
            '    """some class docstring"""\n',
            '    def some(self, a):\n',
            '        """\n',
            '        buhh\n',
            '        """\n',
            '        pass\n',
            '\n',
        ]
        assert_that(docstring_positions(some_file), is_({3: (3, 8)}))

    def test_parse_no_docstring(self):
        some_file = [
            'class Some(object):\n',
            '    def some(self, a):\n',
            '        pass\n',
            '\n',
        ]
        assert_that(docstring_positions(some_file), is_({2: (2, 8)}))

    def test_parse_module_method(self):
        some_file = [
            '@some_decorator\n',
            'def some(self, a):\n',
            '    pass\n',
            '\n',
        ]
        assert_that(docstring_positions(some_file), is_({1: (2, 4)}))

    def test_parse_2_module_methods(self):
        some_file = [
            '@some_decorator\n',
            '\n',
            'def some(self, a):\n',
            '    pass\n',
            '\n',
            'def other(self, a):\n',
            '    pass\n',
            '\n',
        ]
        assert_that(docstring_positions(some_file), is_({1: (3, 4), 6: (6, 4)}))

    def test_parse_newline_in_method_def(self):
        some_file = [
            'def some(a,\n',
            '         b, c):\n',
            '    return a + b + c\n',
        ]
        assert_that(docstring_positions(some_file), is_({1: (2, 4)}))


class TestIntegrationWriting(unittest.TestCase):
    def setUp(self):
        self.old = docstring_writer.write_file
        self.written = Mock()
        docstring_writer.write_file = self.written

    def tearDown(self):
        docstring_writer.write_file = self.old

    @staticmethod
    def in_sample_path(*args):
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(here, 'sample', *args)

    @staticmethod
    def typer_mock(file_names, sorted_findings):
        typer = Mock()
        typer.all_file_names = Mock(return_value=file_names)
        typer.get_sorted_findings = Mock(return_value=sorted_findings)
        return typer

    def test_module_method(self):
        full_file = self.in_sample_path('module_method', 'module_method.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.module_method(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'def some_method(a):\n',
            '    """\n',
            '    :type a: int\n',
            '    :rtype: int\n',
            '    A newline \\n there\n',
            '    and a real one.\n',
            '    """\n',
            '    return a\n',
        ])

    def test_method_in_class(self):
        full_file = self.in_sample_path('method_in_class', 'method_in_class.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.method_in_class(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
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
            '        A = (1, 2)\n',
            '        B, C = A\n',
            '        return self.b + a\n',
        ])

    def test_generator(self):
        full_file = self.in_sample_path('generator', 'generator.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.generator(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'def some_generator():\n',
            '    """:rtype: generator"""\n',
            '    yield 1',
        ])

    def test_classmethod(self):
        full_file = self.in_sample_path('classmethod', 'classmethod.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.class_method(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'class AnotherClass(object):\n',
            '    b = 1\n',
            '\n',
            '    @classmethod\n',
            '    def some_classmethod(cls, a):\n',
            '        """\n',
            '        :type a: int\n',
            '        :rtype: int\n',
            '        """\n',
            '        c = a\n',
            '        return a + cls.b\n',
        ])

    def test_single_type_list(self):
        full_file = self.in_sample_path('list', 'list.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.some_list(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'def get_first_item(a):\n',
            '    """\n',
            '    :type a: list of int or list of list or list of str\n',
            '    :rtype: int or list of int or str\n',
            '    """\n',
            '    return a[0]\n',
        ])

    def test_imported_types(self):
        full_file = self.in_sample_path('imported_types', 'imported_types.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.imported_types(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'def use_imported_types(a, b):\n',
            '    """\n',
            '    :type a: tests.sample.imported_types.to_import.ToImportA\n',
            '    :type b: tests.sample.imported_types.to_import.ToImportB\n',
            '    :rtype: str\n',
            '    """\n',
            "    return 'some result'\n",
        ])

    def test_several_calls(self):
        full_file = self.in_sample_path('several_calls', 'several_calls.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.several_calls(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'def call_me_several_times(a):\n',
            '    """\n',
            '    :type a: int\n',
            '    :rtype: int\n',
            '    """\n',
            '    return a\n',
        ])

    def test_function(self):
        full_file = self.in_sample_path('function', 'function.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.function_finding(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'def some_method(a):\n',
            '    """\n',
            '    :type a: str\n',
            '    :rtype: str\n',
            '    """\n',
            '    return a\n',
            '\n',
            '\n',
            'def a_method(callable_parameter):\n',
            '    """\n',
            '    :type callable_parameter: function\n',
            '    :rtype: str\n',
            '    """\n',
            "    return callable_parameter('hui')\n",
            '\n',
            '\n',
            'def b_method(callable_parameter):\n',
            '    """:rtype: int"""\n',
            '    return callable_parameter(1)\n',
        ])

    def test_dict(self):
        full_file = self.in_sample_path('dict', 'dict.py')
        typing_debugger = self.typer_mock([full_file], sample_findings.dict_finding(full_file))

        docstring_writer.DocstringWriter(typing_debugger).write_all()

        self.written.assert_called_once_with(full_file, [
            'def some_method(a):\n',
            '    """\n',
            '    :type a: dict of (int, str)\n',
            '    :rtype: dict of (int, str)\n',
            '    """\n',
            '    return a'
        ])
