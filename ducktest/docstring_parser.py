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
from abc import abstractmethod, ABCMeta

from mock import Mock

from ducktest import run
from ducktest.type_wrappers import PlainTypeWrapper, ContainerTypeWrapper, MappingTypeWrapper


class WrappedIterator(object):
    """python3 compatibility"""

    def __init__(self, lines):
        self.line_iterator = iter(lines)

    def next_line(self):
        return next(self.line_iterator)


def is_hint_line(line):
    return line.startswith(':type ') or line.startswith(':rtype')


def clean_docstring(text):
    doclines = inspect.cleandoc(text).strip('"').strip('\n').splitlines()
    return [line for line in doclines if not is_hint_line(line)]


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
                docstring_lines = clean_docstring(text)
            else:  # no docstring
                erow = srow
                ecol = scol
                docstring_lines = []
            positions[first_line] = (srow - 1, scol, erow - 1, ecol, docstring_lines)
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


def interesting_file_paths(directories):
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    yield os.path.join(root, file_name)


def module_name(clazz):
    name = clazz.__module__
    if name == '__builtin__' or name == 'builtins':
        return ''
    return name + '.'


def full_name(a_type):
    # try:
    return module_name(a_type) + a_type.__name__
    # except AttributeError:
    #    return ''


def handle_mapper(a_type):
    return [full_name(a_type.own_type) + ' of (' + full_name(list(mapped_type[0])[0].own_type) + ',' + full_name(
        list(mapped_type[1])[0].own_type) + ')' for mapped_type in a_type.mapped_types]


def handle_container_type(a_type):
    return [full_name(a_type.own_type) + ' of ' + full_name(contained.own_type) for contained in a_type.contained_types]


def handle_plain_type(a_type):
    return [full_name(a_type.own_type)]


wrapper_handler = {
    MappingTypeWrapper: handle_mapper,
    ContainerTypeWrapper: handle_container_type,
    PlainTypeWrapper: handle_plain_type,
}


def get_type_names(type_wrappers):
    resulting_wrappers = []
    for type_wrapper in type_wrappers:
        resulting_wrappers += wrapper_handler[type(type_wrapper)](type_wrapper)
    return ' or '.join(sorted(resulting_wrappers))


class DocstringWriter(object):
    def __init__(self, frame_processors, write_directories):
        """:type frame_processors: ducktest.type_wrappers.FrameProcessors"""
        self.write_directories = write_directories
        self.call_types = frame_processors.call_types
        self.return_types = frame_processors.return_types
        # self.all_file_names = sorted(list(self.call_types.file_names() | self.return_types.file_names()))

    def write_all(self):
        for file_path in interesting_file_paths(self.write_directories):
            print file_path
            lines = read_file(file_path)
            parsed_docstrings = parse_docstrings(lines)
            print parsed_docstrings
            for line_number in sorted(parsed_docstrings.keys(), reverse=True):
                call_types = self.call_types.call_types(file_path, line_number)
                to_add = []
                for name in call_types:
                    types = get_type_names(call_types[name])
                    if types:
                        to_add.append(':type {}: {}'.format(name, types))
                return_types = self.return_types.return_types(file_path, line_number)
                type_names = get_type_names(return_types)
                if type_names:
                    to_add.append(':rtype: {}'.format(type_names))
                print to_add


class ConfigMock(object):
    def __init__(self):
        self.top_level_directory = '/home/markus/git/ducktestpy'
        self.discover_tests_in_directories = ['/home/markus/git/ducktestpy/tests/sample']
        self.write_docstrings_in_directories = ['/home/markus/git/ducktestpy/tests/sample']
        self.ignore_call_parameter_names = ['self', 'cls']


if __name__ == '__main__':
    config_mock = ConfigMock()
    typing_debugger, processors = run(config_mock)

    DocstringWriter(processors, config_mock.write_docstrings_in_directories).write_all()
