import tokenize

from ducktest.sphinx_docstring import WrappedIterator


class CodeBlock(object):
    def __init__(self, parent):
        self.parent = parent
        self.children = []
        self.name = None
        self.offset=None

    def with_appended(self, child):
        if child[0] == tokenize.INDENT:
            new = CodeBlock(self)
            self.children.append(new)
            new.children.append(child)
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

    def child_blocks(self):
        for child in self.children:
            if isinstance(child, CodeBlock):
                yield child
                for grandchild in child.child_blocks():
                    yield grandchild

    def append(self, tokens):
        """tokens: CodeBlock or tokens"""
        self.offset = tokens[-1][3][1]
        self.children.append(tokens)

    def tokens(self):
        for child in self.children:
            try:
                for grandchild in child.tokens():
                    yield grandchild
            except AttributeError:
                yield child


class ClassBlock(CodeBlock):
    def __init__(self, parent):
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


def parse_source(lines):
    wrapped_iterator = WrappedIterator(lines)
    start_block = CodeBlock(None)
    head = start_block
    for token in tokenize.generate_tokens(wrapped_iterator.next_line):
        token_type, text, (srow, scol), (erow, ecol), l = token
        head = head.with_appended(token)
    return start_block


if __name__ == '__main__':
    with open('/home/markus/git/ducktestpy/ducktest/setattr_write.py') as f:
        lines = f.readlines()

        print(tokenize.untokenize(parse_source(lines).tokens()))

        start = parse_source(lines)

        print([(block.name, block.offset) for block in start.child_blocks()])

        start.tokens()

        # for definition in parse_source(lines).definitions():
        #    print(definition)
