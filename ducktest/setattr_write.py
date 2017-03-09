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


class Tokens(object):
    def __init__(self, parent, definition):
        self.definition = definition
        self.parent = parent
        self.children = list(definition)

    def add_child(self, child):
        self.children.append(child)

    def definitions(self):
        if self.definition:
            yield self.definition
        for child in self.children:
            if isinstance(child, Tokens):
                for child_definition in child.definitions():
                    if child_definition:
                        yield child_definition

    def tokens(self):
        for child in self.children:
            if isinstance(child, Tokens):
                for token in child.tokens():
                    yield token
            else:
                yield child


definitions = [
    (tokenize.NAME, 'def'),
    (tokenize.NAME, 'class'),
    (tokenize.OP, '@')
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


if __name__ == '__main__':

    with open('/home/markus/git/ducktestpy/ducktest/setattr_write.py') as f:
        lines = f.readlines()
        parsed = parse_source(lines)
        listed = list(parsed.tokens())
        # for item in listed:
        #    print(item)
        # print(tokenize.untokenize(listed))

        for definition in parse_source(lines).definitions():
            print(definition)