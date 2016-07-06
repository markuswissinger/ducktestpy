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


class WrappedIterator(object):
    """python3 compatibility"""

    def __init__(self, lines):
        self.line_iterator = iter(lines)

    def next_line(self):
        return next(self.line_iterator)


def docstring_positions(lines):
    """:returns a dictionary {line_number_of_def_statement: (write_docstring_to_line_index, docstring_indent)}"""
    positions = {}
    state = ''
    prev_token_type = None
    maybe_first_line = None
    first_line = None
    wrapped_iterator = WrappedIterator(lines)
    for token_type, text, (srow, scol), (erow, ecol), l in tokenize.generate_tokens(wrapped_iterator.next_line):
        # print ','.join([str(item) for item in [token_type, text, srow, scol]])
        if prev_token_type == tokenize.INDENT and state == 'in_function':
            positions[first_line] = (srow - 1, scol)
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


def write_file(file_name, lines):
    with open(file_name, 'w') as f:
        f.writelines(lines)


class DocstringWriter(object):
    def __init__(self, typer):
        self.typer = typer

    def write_all(self):
        for file_name in self.typer.all_file_names():
            modified_file_lines = self._modified_file_lines(file_name)
            write_file(file_name, modified_file_lines)

    def _modified_file_lines(self, file_name):
        lines = read_file(file_name)
        positions = docstring_positions(lines)
        for finding in self.typer.get_sorted_findings(file_name):
            try:
                doc_index, doc_indent = positions[finding.first_line_number]
                modified = self._modified_docstring(finding, doc_indent)
                lines = lines[:doc_index] + modified + lines[doc_index + self._number_doclines(finding.docstring):]
            except KeyError:  # parsing fails (e.g. for <genexp>)
                continue
        return lines

    @staticmethod
    def _number_doclines(docstring):
        if docstring is None:
            return 0
        return len(docstring.split('\n'))

    @staticmethod
    def _clean_doclines(docstring):
        if docstring is None:
            return []
        lines = [line.strip() for line in docstring.split('\n')]
        if lines[0] == '':
            lines = lines[1:]
        try:
            if lines[-1] == '':
                lines = lines[0:-1]
        except IndexError:
            pass
        clean_lines = [line for line in lines if not line.startswith(':type') and not line.startswith(':rtype')]
        return clean_lines

    @staticmethod
    def _unique_type_names(type_wrappers):
        the_types = set()
        for wrapper in type_wrappers:
            for some_type in DocstringTypeWrapper(wrapper).contained():
                the_types.add(some_type)
        return ' or '.join(sorted(list(the_types)))

    def _modified_docstring(self, finding, indent):
        new_lines = []
        for call_parameter_name, call_types in finding.call_parameters():
            new_lines.append(':type ' + call_parameter_name + ': ' + self._unique_type_names(call_types))
        if finding.return_types:
            new_lines.append(':rtype: ' + self._unique_type_names(finding.return_types))
        new_lines.extend(self._clean_doclines(finding.docstring))

        if len(new_lines) == 1:
            return [indent * ' ' + '"""' + new_lines[0] + '"""\n']

        new_lines = ['"""'] + new_lines + ['"""']
        return [indent * ' ' + line + '\n' for line in new_lines]


class DocstringTypeWrapper(object):
    def __init__(self, type_wrapper):
        self.type_wrapper = type_wrapper

    @staticmethod
    def _module_name(clazz):
        name = clazz.__module__
        if name == '__builtin__' or name == 'builtins':
            return ''
        return name + '.'

    def _full_name(self, a_type):
        try:
            return self._module_name(a_type) + a_type.__name__
        except AttributeError:
            return ''

    def contained(self):
        full_name = self._full_name(self.type_wrapper.type)
        if self.type_wrapper.contained_types or self.type_wrapper.mapped_types:
            return [full_name + ' of ' + self._full_name(contained) for contained in self.type_wrapper.contained_types
                    if
                    contained] + [full_name + ' of ({}, {})'.format(self._full_name(key), self._full_name(value)) for
                                  key, value in self.type_wrapper.mapped_types if (key and value)]

        return [full_name]

    def __str__(self):
        full_name = self._full_name(self.type_wrapper.type)
        if self.type_wrapper.contained_types:
            return ' or '.join(
                [full_name + ' of ' + self._full_name(contained) for contained in self.type_wrapper.contained_types if
                 contained])
        return full_name
