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
import tokenize
import unittest

from ducktest.type_wrappers import FrameProcessors


class WrappedIterator(object):
    """python3 compatibility"""

    def __init__(self, lines):
        self.line_iterator = iter(lines)

    def next_line(self):
        return next(self.line_iterator)


def docstring_positions(lines):
    """:returns a dictionary {first_line_number: (write_docstring_to_line_index, docstring_indent)}"""
    positions = {}
    docstrings = {}
    state = ''
    prev_token_type = None
    maybe_first_line = None
    first_line = None
    wrapped_iterator = WrappedIterator(lines)
    for token_type, text, (srow, scol), (erow, ecol), l in tokenize.generate_tokens(wrapped_iterator.next_line):
        print ','.join([str(item) for item in [token_type, text, srow, scol]])
        if prev_token_type == tokenize.INDENT and state == 'in_function':
            positions[first_line] = (srow - 1, scol)
            if token_type == tokenize.STRING:
                docstrings[first_line] = text
            else:
                docstrings[first_line] = None
            state = 'docstring_position_found'
        if text == '@':
            maybe_first_line = srow
        if token_type == tokenize.INDENT or token_type == tokenize.DEDENT:
            maybe_first_line = None
        if text == 'def' and token_type == tokenize.NAME:
            first_line = maybe_first_line or srow
            state = 'in_function'
        prev_token_type = token_type
    return positions, docstrings


def read_file(file_name):
    with open(file_name) as f:
        return f.readlines()


class Config(object):
    def __init__(self):
        here = os.path.dirname(os.path.abspath(__file__))
        self.top_level_directory = os.path.split(here)[0]
        self.discover_tests_in_directories = [here]
        self.write_docstrings_in_directories = [here]
        self.ignore_call_parameter_names = ['self', 'cls']


class TestParser(unittest.TestCase):
    def test_some(self):
        lines = read_file('parse_example.py')
        positions, docstrings = docstring_positions(lines)

        print positions
        print docstrings
