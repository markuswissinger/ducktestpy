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

import unittest

from hamcrest import assert_that, is_
from mock import Mock

from ducktest import run, docstring_writer
from ducktest.docstring_writer import docstring_positions
from tests.test_typer import ConfigMock


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

    def test_module_method(self):
        conf = ConfigMock('module_method')
        typing_debugger = run(conf)
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
