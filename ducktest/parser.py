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

import itertools
import tokenize

from ducktest.sphinx_docstring import WrappedIterator


class CodeLine(object):
    def __init__(self, transfer=None):
        self.children = transfer if transfer else []

    def append(self, token):
        self.children.append(token)

    def __eq__(self, other):
        return isinstance(other, CodeLine) and self.children == other.children

    def __repr__(self):
        return '{}(transfer={})'.format(type(self).__name__, repr(self.children))

    def on_parse_blocks(self, head, ignore_next_indent):
        head.append(self)
        return head, ignore_next_indent

    def tokens(self):
        for child in self.children:
            yield child


class DedentLine(CodeLine):
    def on_parse_blocks(self, head, ignore_next_indent):
        head.append(self)
        return head.parent, ignore_next_indent


class IndentLine(CodeLine):
    def on_parse_blocks(self, head, ignore_next_indent):
        if ignore_next_indent:
            head.append(self)
            return head, False
        new_block = CodeBlock(head)
        head.append(self)
        head.append(new_block)
        return new_block, False


class CodeBlock(object):
    def __init__(self, parent):
        self.parent = parent
        self.children = []

    def append(self, child):
        self.children.append(child)

    def __repr__(self):
        return repr(self.children)

    def tokens(self):
        for gen in itertools.chain(child.tokens() for child in self.children):
            for token in gen:
                yield token


class ClassBlock(CodeBlock):
    def __init__(self, name, parent):
        super(ClassBlock, self).__init__(parent)
        self.name = name


class DefBlock(CodeBlock):
    def __init__(self, name, parent):
        super(DefBlock, self).__init__(parent)
        self.name = name


class ClassLine(CodeLine):
    def __init__(self, **kwargs):
        super(ClassLine, self).__init__(**kwargs)
        self.name = None

    def on_parse_blocks(self, head, ignore_next_indent):
        new_block = ClassBlock(self.name, head)
        head.append(new_block)
        new_block.append(self)
        return new_block, True

    def append(self, token):
        if not self.name:
            self.name = token[1]
        super(ClassLine, self).append(token)


class DefLine(CodeLine):
    def __init__(self, **kwargs):
        super(DefLine, self).__init__(**kwargs)
        self.name = None

    def on_parse_blocks(self, head, ignore_next_indent):
        new_block = DefBlock(self.name, head)
        head.append(new_block)
        new_block.append(self)
        return new_block, True

    def append(self, token):
        if not self.name:
            self.name = token[1]
        super(DefLine, self).append(token)


def new_line(current_line, lines):
    if current_line.children:
        lines.append(current_line)
        return CodeLine()
    return current_line


def parse_lines(lines):
    wrapped_iterator = WrappedIterator(lines)
    parsed_lines = []
    current_line = CodeLine()
    for token in tokenize.generate_tokens(wrapped_iterator.next_line):
        token_type, text, (srow, scol), (erow, ecol), l = token
        if token_type == tokenize.INDENT:
            current_line = new_line(current_line, parsed_lines)
            current_line = IndentLine(transfer=current_line.children)
            current_line.append(token)
            current_line = new_line(current_line, parsed_lines)
            continue
        if token_type == tokenize.DEDENT:
            current_line = new_line(current_line, parsed_lines)
            current_line = DedentLine(transfer=current_line.children)
            current_line.append(token)
            current_line = new_line(current_line, parsed_lines)
            continue

        current_line.append(token)
        if (token_type, text) == (tokenize.NAME, 'class'):
            current_line = ClassLine(transfer=current_line.children)
        if (token_type, text) == (tokenize.NAME, 'def'):
            current_line = DefLine(transfer=current_line.children)
        if token_type == tokenize.NEWLINE or (token_type, text) == (54, '\n'):
            current_line = new_line(current_line, parsed_lines)
    return parsed_lines


class SignatureParser(object):
    def __init__(self):
        self.count = {item: 0 for item in ('(', ')', '{', '}', '[', ']')}
        self.signature_started = False
        self._interpret = self.initial
        self.name_positions = []
        self.hint_start_positions = []
        self.hint_end_positions = []

    def interpret(self, index, token):
        text = token[1]
        if text in self.count:
            self.count[text] += 1
        self._interpret(index, token)

    def initial(self, index, token):
        text = token[1]
        if text == 'def':
            self._interpret = self.wait_for_name

    def wait_for_name(self, index, token):
        if token[1] == '(':
            self.signature_started = True
        if self.end_of_signature():
            self._interpret = self.do_pass
        if not self.in_signature():
            return
        token_type = token[0]
        if token_type == tokenize.NAME:
            self.name_positions.append(index)
            self._interpret = self.wait_for_hint_start

    def wait_for_hint_start(self, index, token):
        if self.end_of_signature():
            self.hint_start_positions.append(index)
            self.hint_end_positions.append(index)
            self._interpret = self.do_pass
        if not self.in_signature():
            return
        if token[1] == ',':
            self.hint_start_positions.append(index)
            self.hint_end_positions.append(index)
            self._interpret = self.wait_for_name
        if token[1] == ':':
            self._interpret = self.read_hint_start

    def read_hint_start(self, index, token):
        self.hint_start_positions.append(index)
        self._interpret = self.wait_for_hint_end

    def wait_for_hint_end(self, index, token):
        if self.end_of_signature():
            self.hint_end_positions.append(index)
            self._interpret = self.do_pass
        if not self.in_signature():
            return
        if token[1] == ',':
            self.hint_end_positions.append(index)
            self._interpret = self.wait_for_name

    def do_pass(self, index, token):
        pass

    def in_signature(self):
        return self.count['('] - self.count[')'] == 1 \
               and self.count['['] - self.count[']'] == 0 \
               and self.count['{'] - self.count['}'] == 0

    def end_of_signature(self):
        return self.count['('] - self.count[')'] == 0 and self.signature_started

    def parse_signature(self, def_line):
        for index, token in enumerate(def_line.children):
            # token_type, text, start, end, line = token
            self.interpret(index, token)


def parse_logical_lines(lines):
    wrapped_iterator = WrappedIterator(lines)
    parsed_lines = []
    current_line = CodeLine()
    for token in tokenize.generate_tokens(wrapped_iterator.next_line):
        token_type, text, (srow, scol), (erow, ecol), l = token
        current_line.append(token)
        if (token_type, text) == (tokenize.NAME, 'class'):
            current_line = ClassLine(transfer=current_line.children)
        if (token_type, text) == (tokenize.NAME, 'def'):
            current_line = DefLine(transfer=current_line.children)
        if token_type == tokenize.NEWLINE:
            current_line = new_line(current_line, parsed_lines)
    return parsed_lines


def parse_blocks(parsed_lines):
    start_block = CodeBlock(None)
    head = start_block
    ignore_next_indent = False
    for line in parsed_lines:
        head, ignore_next_indent = line.on_parse_blocks(head, ignore_next_indent)
    return start_block
