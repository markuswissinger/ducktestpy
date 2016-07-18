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

import tokenize
import unittest


class WrappedIterator(object):
    """python3 compatibility"""

    def __init__(self, lines):
        self.line_iterator = iter(lines)

    def next_line(self):
        return next(self.line_iterator)


def docstring_positions(lines):
    """:returns a dictionary {line_number_of_def_statement: (write_docstring_to_line_index, docstring_indent)}"""
    positions = {}
    docstrings = {}
    state = ''
    prev_token_type = None
    first_line = None
    wrapped_iterator = WrappedIterator(lines)
    for token_type, text, (srow, scol), (erow, ecol), l in tokenize.generate_tokens(wrapped_iterator.next_line):
        print ','.join([str(item) for item in [token_type, text, srow, scol]])
        if prev_token_type == tokenize.INDENT and state == 'in_function':
            positions[first_line] = (srow - 1, scol)
            docstrings[first_line] = text
            state = 'docstring_position_found'
        if text == 'def' and token_type == tokenize.NAME:
            state = 'in_function'

        prev_token_type = token_type
    return positions, docstrings


def read_file(file_name):
    with open(file_name) as f:
        return f.readlines()


class TestParser(unittest.TestCase):
    def test_some(self):
        lines = read_file('parse_example.py')
        positions, docstrings=docstring_positions(lines)

        print positions
        print docstrings
