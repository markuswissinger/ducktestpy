import tokenize

from ducktest.sphinx_docstring import WrappedIterator


def hui():
    pass


A = 'HUI' \
    'UIUI'


class Some(object):
    def __setattr__(self, name, value):
        super(Some, self).__setattr__(name, value)

    @staticmethod
    def noop():
        pass

    def some(self, a=hui):
        pass


class LineDefinition(object):
    def __init__(self, tokens):
        self.tokens = tokens


class MethodDefinition(LineDefinition):
    def_token = (tokenize.NAME, 'def')


class ClassDefinition(LineDefinition):
    def_token = (tokenize.NAME, 'class')


def_classes = (
    MethodDefinition,
    ClassDefinition,
)


def create_definition(definition_tokens):
    for def_class in def_classes:
        if def_class.def_token in definition_tokens:
            return def_class(definition_tokens)
    return LineDefinition(definition_tokens)


class Tokens(object):
    def __init__(self, parent, definition):
        self.definition = create_definition(definition)
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def definitions(self):
        if self.definition:
            yield self.definition.tokens
        for child in self.children:
            if isinstance(child, Tokens):
                for child_definition in child.definitions():
                    if child_definition:
                        yield child_definition

    def tokens(self):
        for child in self.definition.tokens + self.children:
            if isinstance(child, Tokens):
                for token in child.tokens():
                    yield token
            else:
                yield child


definitions = [
    (tokenize.NAME, 'def'),
    (tokenize.NAME, 'class'),
    (tokenize.OP, '@'),
]


def parse_source(lines):
    """:returns a dictionary {first_method_line_number:
    (start_line_index, start_coloumn, end_line_index, end_coloumn, docstring)}"""
    wrapped_iterator = WrappedIterator(lines)
    definition_tokens = []
    start_block = Tokens(None, [])
    current_block = start_block
    for token in tokenize.generate_tokens(wrapped_iterator.next_line):
        token_type, text, (srow, scol), (erow, ecol), l = token
        # token = token_type, text, (srow, scol), (erow, ecol), ''
        # all but l are necessary for output
        if definition_tokens or (token_type, text) in definitions:
            definition_tokens.append(token)
        else:
            current_block.add_child(token)

        if token_type == tokenize.INDENT:
            new_block = Tokens(current_block, definition_tokens)
            definition_tokens = []
            current_block.add_child(new_block)
            current_block = new_block
        if token_type == tokenize.DEDENT:
            current_block = current_block.parent
    return start_block


class CodeBlock(object):
    def __init__(self, parent):
        self.parent = parent
        self.children = []

    def with_appended(self, child):
        if child[0] == tokenize.INDENT:
            new = CodeBlock(self)
            self.children.append(new)
            return new
        if child[0] == tokenize.DEDENT:
            self.children.append(child)
            return self.parent
        if child[:2] == (tokenize.NAME, 'class'):
            new = ClassBlock(self)
            self.children.append(new)
            new.children.append(child)
            return new
        if child[:2] == (tokenize.NAME, 'def'):
            new = MethodBlock(self)
            self.children.append(new)
            new.children.append(child)
            return new
        if child[:2] == (tokenize.OP, '@'):
            new = DecoratedBlock(self)
            self.children.append(new)
            new.children.append(child)
            return new
        self.children.append(child)
        return self

    def tokens(self):
        for child in self.children:
            try:
                for grandchild in child.tokens():
                    yield grandchild
            except AttributeError:
                yield child


class ClassBlock(CodeBlock):
    def __init__(self, parent):
        self.name = None
        self.expected_indent = True
        super(ClassBlock, self).__init__(parent)

    def with_appended(self, child):
        if not self.name:
            self.name = child[1]

        if child[0] == tokenize.INDENT:
            if self.expected_indent:
                self.expected_indent = False
            else:
                new = CodeBlock(self)
                self.children.append(new)
                return new
        if child[0] == tokenize.DEDENT:
            self.children.append(child)
            return self.parent
        if child[:2] == (tokenize.NAME, 'def'):
            new = MethodBlock(self)
            self.children.append(new)
            new.children.append(child)
            return new
        if child[:2] == (tokenize.OP, '@'):
            new = DecoratedBlock(self)
            self.children.append(new)
            new.children.append(child)
            return new
        self.children.append(child)
        return self


class MethodBlock(CodeBlock):
    def __init__(self, parent):
        self.name = None
        self.expected_indent = True
        super(MethodBlock, self).__init__(parent)

    def with_appended(self, child):
        if not self.name:
            self.name = child[1]

        if child[0] == tokenize.INDENT:
            if self.expected_indent:
                self.expected_indent = False
            else:
                new = CodeBlock(self)
                self.children.append(new)
                return new
        if child[0] == tokenize.DEDENT:
            self.children.append(child)
            return self.parent
        self.children.append(child)
        return self


class DecoratedBlock(CodeBlock):
    def __init__(self, parent):
        self.name = None
        self._got_def = False
        self.expected_indent = True
        super(DecoratedBlock, self).__init__(parent)

    def with_appended(self, child):
        if not self.name and self._got_def:
            self.name = child[1]
        if child[:2] == (tokenize.NAME, 'def'):
            self._got_def = True

        if child[0] == tokenize.INDENT:
            if self.expected_indent:
                self.expected_indent = False
            else:
                new = CodeBlock(self)
                self.children.append(new)
                return new
        if child[0] == tokenize.DEDENT:
            self.children.append(child)
            return self.parent
        self.children.append(child)
        return self


def parse_b(lines):
    wrapped_iterator = WrappedIterator(lines)
    start_block = CodeBlock(None)
    head = start_block
    def_line = []
    for token in tokenize.generate_tokens(wrapped_iterator.next_line):
        token_type, text, (srow, scol), (erow, ecol), l = token

        head = head.with_appended(token)
    return start_block


if __name__ == '__main__':
    with open('/home/markus/git/ducktestpy/ducktest/setattr_write.py') as f:
        lines = f.readlines()

        print(tokenize.untokenize(parse_b(lines).tokens()))

        start = parse_b(lines)

        start.tokens()

        # for definition in parse_source(lines).definitions():
        #    print(definition)
