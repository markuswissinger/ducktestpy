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
import inspect
import os
import tokenize

from mock import Mock


class WrappedIterator(object):
    """python3 compatibility"""

    def __init__(self, lines):
        self.line_iterator = iter(lines)

    def next_line(self):
        return next(self.line_iterator)


def parse_docstrings(lines):
    """:returns a dictionary {first_method_line_number:
    (start_line_index, start_coloumn, end_line_index, end_coloumn, docstring)}"""
    positions = {}
    state = ''
    prev_token_type = None
    maybe_first_line = None
    first_line = None
    wrapped_iterator = WrappedIterator(lines)
    for token_type, text, (srow, scol), (erow, ecol), l in tokenize.generate_tokens(wrapped_iterator.next_line):
        # print ','.join([str(item) for item in [token_type, text, srow, scol]])
        if prev_token_type == tokenize.INDENT and state == 'in_function':
            if token_type == tokenize.STRING:
                docstring = inspect.cleandoc(text).strip('"').strip('\n').splitlines()
            else:  # no docstring
                erow = srow
                ecol = scol
                docstring = ''
            positions[first_line] = (srow - 1, scol, erow - 1, ecol, docstring)
            state = 'docstring_position_found'
        if text == '@':
            maybe_first_line = srow
        if token_type == tokenize.INDENT or token_type == tokenize.DEDENT:
            maybe_first_line = None
        if text == 'def' and token_type == tokenize.NAME:
            first_line = maybe_first_line or srow
            state = 'in_function'
        prev_token_type = token_type
    return positions


def read_file(file_name):
    with open(file_name) as f:
        return f.readlines()


class DocstringWriter(object):
    def __init__(self, frame_processors, write_directories):
        """:type frame_processors: ducktest.type_wrappers.FrameProcessors"""
        self.write_directories = write_directories
        self.call_types = frame_processors.call_types
        self.return_types = frame_processors.return_types
        # self.all_file_names = sorted(list(self.call_types.file_names() | self.return_types.file_names()))

    def write_all(self):
        for directory in self.write_directories:
            for root, _, files in os.walk(directory):
                for file_name in files:
                    if file_name.endswith('.py'):
                        file_path = os.path.join(root, file_name)
                        print file_path
                        lines = read_file(file_path)
                        print parse_docstrings(lines)


if __name__ == '__main__':
    DocstringWriter(Mock(), ['/home/markus/git/ducktestpy/ducktest', ]).write_all()
