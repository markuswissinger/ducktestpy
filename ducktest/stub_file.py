import tokenize
from collections import OrderedDict
from six import iteritems

from ducktest.sphinx_docstring import WrappedIterator, read_file, interesting_file_paths


class DefStubLine(object):
    def __init__(self, indent):
        self.indent = indent
        self.name = None
        self.call_signature = ''
        self.return_signature = 'None'
        self.has_body = False

    def ellipsis(self):
        if self.has_body:
            return ''
        return ' ...'

    def append(self, tokentype, text):
        if tokentype == tokenize.NAME and not self.name:
            self.name = text

    def add_call(self, call_types):
        entries = []
        for name, types in iteritems(call_types):
            if len(types) == 0:
                entries.append(name)
            elif len(types) == 1:
                entries.append(name + ": '" + types.pop().own_type.__name__ + "'")
            else:
                entries.append(name + ': ' + "'Union[{}]'".format(
                    ', '.join(sorted([entry.own_type.__name__ for entry in types]))
                ))
        self.call_signature = ', '.join(entries)

    def add_return(self, return_types):
        if len(return_types) == 0:
            self.return_signature = 'None'
        elif len(return_types) == 1:
            self.return_signature = return_types.pop().own_type.__name__
        else:
            self.return_signature = 'Union[{}]'.format(
                ', '.join(sorted([entry.own_type.__name__ for entry in return_types])))

    def __str__(self):
        return "{indent}def {name}({call_signature}) -> {return_signature}:{ellipsis}\n".format(
            indent=' ' * self.indent,
            name=self.name,
            call_signature=self.call_signature,
            return_signature=self.return_signature,
            ellipsis=self.ellipsis(),
        )


class ClassStubLine(object):
    def __init__(self, indent):
        self.indent = indent
        self.name = None
        self.tokens = []
        self.has_body = False

    def add_call(self, call_types):
        pass

    def add_return(self, return_types):
        pass

    def ellipsis(self):
        if self.has_body:
            return ''
        return ' ...'

    def append(self, tokentype, text):
        if tokentype == tokenize.NAME and not self.name:
            self.name = text
        elif text == ',':
            self.tokens.append(', ')
        else:
            self.tokens.append(text)

    def __str__(self):
        tokens = ''.join(self.tokens).rstrip()
        return '{}class {}{}{}\n'.format(self.indent * ' ', self.name, tokens, self.ellipsis())


class ImportStubLine(object):
    indent = 0

    def __init__(self, text):
        self.items = [text]

    def append(self, token_type, text):
        self.items.append(text)

    def add_call(self, call_types):
        pass

    def add_return(self, return_types):
        pass

    def __str__(self):
        return ' '.join(self.items)


NOT_IN_LINE = 0
INLINE = 1
IN_IMPORT = 2


def parse_source(lines):
    """
    :returns a OrderedDictionary {line number: indent, def/class, name)"""
    wrapped_iterator = WrappedIterator(lines)
    state = NOT_IN_LINE
    stubs = OrderedDict()
    stub = None

    for token_type, text, (srow, scol), (erow, ecol), l in tokenize.generate_tokens(wrapped_iterator.next_line):
        if token_type == tokenize.INDENT and state == INLINE:
            state = NOT_IN_LINE
        if token_type == tokenize.NEWLINE and state == IN_IMPORT:
            stub.append(token_type, text)
            state = NOT_IN_LINE
        if state == INLINE or state == IN_IMPORT:
            stub.append(token_type, text)
        if text == 'def' and token_type == tokenize.NAME:
            state = INLINE
            stub = DefStubLine(scol)
            stubs[srow] = stub
        if text == 'class' and token_type == tokenize.NAME:
            state = INLINE
            stub = ClassStubLine(scol)
            stubs[srow] = stub
        if (text == 'from' or text == 'import') and scol == 0:
            state = IN_IMPORT
            stub = ImportStubLine(text)
            stubs[srow] = stub
    return stubs


class StubFileWriter(object):
    def __init__(self, call_types, return_types, configuration):
        self.write_directories = configuration.write_docstrings_in_directories
        self.ignore_call_parameter_names = configuration.ignore_call_parameter_names
        self.call_types = call_types
        self.return_types = return_types

    def write_all(self):
        for file_path in interesting_file_paths(self.write_directories):
            source_lines = read_file(file_path)
            stub_positions = parse_source(source_lines)
            stub_file_lines = []
            for stub_line_number, stub_position in iteritems(stub_positions):
                called = self.call_types.call_types(file_path, stub_line_number)
                for name in called.keys():
                    if name in self.ignore_call_parameter_names:
                        called[name] = set([])
                returned = self.return_types.return_types(file_path, stub_line_number)
                if called or returned or isinstance(stub_position, ClassStubLine) or isinstance(stub_position,
                                                                                                ImportStubLine):
                    stub_position.add_call(called)
                    stub_position.add_return(returned)
                    stub_file_lines.append(stub_position)

            print(stub_file_lines)

            for first, second in zip(stub_file_lines[:-1], stub_file_lines[1:]):
                if first.indent < second.indent:
                    first.has_body = True

            with open(file_path + 'i', 'w') as f:
                f.writelines([str(line) for line in stub_file_lines])
