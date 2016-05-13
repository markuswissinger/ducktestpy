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

from ducktest.docstring_writer import docstring_positions


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
