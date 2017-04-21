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

from ducktest.base import PlainTypeWrapper, ContainerTypeWrapper, MappingTypeWrapper


class WrappedIterator(object):
    """python3 compatibility"""

    def __init__(self, lines):
        self.line_iterator = iter(lines)

    def next_line(self):
        return next(self.line_iterator)


def is_hint_line(line):
    return line.startswith(':type ') or line.startswith(':rtype')


INITIAL = 0
IN_FUNCTION = 1
DOCSTRING_POSITION_FOUND = 2


def parse_docstrings(lines):
    """:returns a dictionary {first_method_line_number:
    (start_line_index, start_coloumn, end_line_index, end_coloumn, docstring)}"""
    positions = {}
    state = INITIAL
    prev_token_type = None
    maybe_first_line = None
    first_line = None
    wrapped_iterator = WrappedIterator(lines)
    for token_type, text, (srow, scol), (erow, ecol), l in tokenize.generate_tokens(wrapped_iterator.next_line):
        if state == IN_FUNCTION and prev_token_type == tokenize.INDENT:
            if token_type == tokenize.STRING:
                docstring_lines = inspect.cleandoc(text).splitlines()
            else:  # method has no docstring
                erow = srow
                ecol = scol
                docstring_lines = []
            positions[first_line] = (srow, scol, erow, ecol, docstring_lines)
            state = DOCSTRING_POSITION_FOUND
        if text == '@':
            maybe_first_line = srow
        if token_type == tokenize.INDENT or token_type == tokenize.DEDENT:
            maybe_first_line = None
        if text == 'def' and token_type == tokenize.NAME:
            first_line = maybe_first_line or srow
            state = IN_FUNCTION
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
    return module_name(a_type) + a_type.__name__


def handle_mapper(a_type):
    if a_type.mapped_types:
        return [full_name(a_type.own_type) + ' of ' + full_name(list(mapped_type[0])[0].own_type) + ',' + full_name(
            list(mapped_type[1])[0].own_type) for mapped_type in a_type.mapped_types]
    return [full_name(a_type.own_type)]


def handle_container_type(a_type):
    if a_type.contained_types:
        return [full_name(a_type.own_type) + ' of ' + full_name(contained.own_type) for contained in
                a_type.contained_types]
    return [full_name(a_type.own_type)]


def handle_plain_type(a_type):
    return [full_name(a_type.own_type)]


wrapper_handler = {
    MappingTypeWrapper: handle_mapper,
    ContainerTypeWrapper: handle_container_type,
    PlainTypeWrapper: handle_plain_type,
}


def get_type_names(type_wrappers):
    resulting_wrappers = []
    non_plain_names = set()
    for type_wrapper in type_wrappers:
        resulting_wrappers += wrapper_handler[type(type_wrapper)](type_wrapper)
        if type(type_wrapper) != PlainTypeWrapper:
            non_plain_names.add(full_name(type_wrapper.own_type))
    return ' or '.join(sorted(list(set(resulting_wrappers))))


def write_file(file_name, lines):
    with open(file_name, 'w') as f:
        f.writelines(lines)


class DocstringWriter(object):
    def __init__(self, call_types, return_types, configuration):
        self.write_directories = configuration.write_docstrings_in_directories
        self.ignore_call_parameter_names = configuration.ignore_call_parameter_names
        self.call_types = call_types
        self.return_types = return_types

    def write_all(self):
        for file_path in interesting_file_paths(self.write_directories):
            lines = read_file(file_path)
            parsed_docstrings = parse_docstrings(lines)
            for def_line_number in sorted(parsed_docstrings.keys(), reverse=True):
                call_types = self.call_types.call_types(file_path, def_line_number)
                to_add = []
                for name in call_types:
                    if name in self.ignore_call_parameter_names:
                        continue
                    types = get_type_names(call_types[name])
                    if types:
                        to_add.append(':type {}: {}'.format(name, types))

                return_types = self.return_types.return_types(file_path, def_line_number)
                type_names = get_type_names(return_types)
                if type_names:
                    to_add.append(':rtype: {}'.format(type_names))

                srow, scol, erow, ecol, doclines = parsed_docstrings[def_line_number]

                clean_doclines, marker = process_doclines(doclines)

                full_docstring = to_add + clean_doclines
                if full_docstring:
                    if len(full_docstring) == 1:
                        new_docstring = [marker + full_docstring[0] + marker]
                    else:
                        new_docstring = [marker] + full_docstring + [marker]
                else:
                    new_docstring = []
                formatted = [' ' * scol + line + '\n' for line in new_docstring]
                lines = lines[:srow - 1] + formatted + lines[srow + len(doclines) - 1:]
            write_file(file_path, lines)


def process_doclines(doclines):
    if not doclines:
        return [], '"""'
    if doclines[0].startswith("'''"):
        marker = "'"
    else:
        marker = '"'

    if doclines[0] == marker * 3:
        doclines = doclines[1:]
    else:
        doclines[0] = doclines[0].lstrip(marker)

    if doclines[-1] == marker * 3:
        doclines = doclines[:-1]
    else:
        doclines[-1] = doclines[-1].rstrip(marker)

    return [docline for docline in doclines if not is_hint_line(docline)], marker * 3
