import itertools
import os
import sys
import tokenize
import unittest

from hamcrest import assert_that, is_

from ducktest.parser import parse_lines, parse_blocks, ClassLine, IndentLine, DedentLine, CodeLine, DefLine

python_major = int(sys.version.split('.')[0])

path = os.path.split(__file__)[0]


def in_path(a_file):
    return os.path.join(path, a_file)


class TestParser(unittest.TestCase):
    def test_full_file(self):
        with open(in_path('to_parse.py')) as f:
            lines = f.readlines()
            parsed = parse_lines(lines)
            assert_that(parsed, is_([
                ClassLine(transfer=[
                    (1, 'class', (1, 0), (1, 5), 'class Some(object):\n'),
                    (1, 'Some', (1, 6), (1, 10), 'class Some(object):\n'),
                    (51, '(', (1, 10), (1, 11), 'class Some(object):\n'),
                    (1, 'object', (1, 11), (1, 17), 'class Some(object):\n'),
                    (51, ')', (1, 17), (1, 18), 'class Some(object):\n'),
                    (51, ':', (1, 18), (1, 19), 'class Some(object):\n'),
                    (4, '\n', (1, 19), (1, 20), 'class Some(object):\n')
                ]),
                IndentLine(transfer=[
                    (5, '    ', (2, 0), (2, 4), '    def __init__(self, a):\n')],
                ),
                DefLine(transfer=[
                    (1, 'def', (2, 4), (2, 7), '    def __init__(self, a):\n'),
                    (1, '__init__', (2, 8), (2, 16), '    def __init__(self, a):\n'),
                    (51, '(', (2, 16), (2, 17), '    def __init__(self, a):\n'),
                    (1, 'self', (2, 17), (2, 21), '    def __init__(self, a):\n'),
                    (51, ',', (2, 21), (2, 22), '    def __init__(self, a):\n'),
                    (1, 'a', (2, 23), (2, 24), '    def __init__(self, a):\n'),
                    (51, ')', (2, 24), (2, 25), '    def __init__(self, a):\n'),
                    (51, ':', (2, 25), (2, 26), '    def __init__(self, a):\n'),
                    (4, '\n', (2, 26), (2, 27), '    def __init__(self, a):\n'),
                ]),
                IndentLine(transfer=[
                    (5, '        ', (3, 0), (3, 8), '        """a docstring"""\n'),
                ]),
                CodeLine(transfer=[
                    (3, '"""a docstring"""', (3, 8), (3, 25), '        """a docstring"""\n'),
                    (4, '\n', (3, 25), (3, 26), '        """a docstring"""\n'),
                ]),
                CodeLine(transfer=[
                    (1, 'self', (4, 8), (4, 12), '        self.a = a\n'),
                    (51, '.', (4, 12), (4, 13), '        self.a = a\n'),
                    (1, 'a', (4, 13), (4, 14), '        self.a = a\n'),
                    (51, '=', (4, 15), (4, 16), '        self.a = a\n'),
                    (1, 'a', (4, 17), (4, 18), '        self.a = a\n'),
                    (4, '\n', (4, 18), (4, 19), '        self.a = a\n'), ]),
                DedentLine(transfer=[
                    (6, '', (5, 0), (5, 0), ''),
                ]),
                DedentLine(transfer=[
                    (6, '', (5, 0), (5, 0), ''),
                ])]
            ))

    def test_round_trip(self):
        with open(in_path('to_parse.py')) as f:
            lines = f.readlines()
            parsed = parse_lines(lines)
            root_block = parse_blocks(parsed)
        with open(in_path('to_parse.py')) as f:
            assert_that(tokenize.untokenize(root_block.tokens()), is_(''.join(list(f.readlines()))))

    def test_compare_line_and_block_tokens(self):
        with open(in_path('to_parse.py')) as f:
            lines = f.readlines()
            parsed = parse_lines(lines)
            root_block = parse_blocks(parsed)
        line_tokens = list(itertools.chain(*(line.tokens() for line in parsed)))
        block_tokens = list(root_block.tokens())
        assert_that(block_tokens, is_(line_tokens))

    def test_parse_line_tokens_roundtrip(self):
        with open(in_path('to_parse.py')) as f:
            lines = list(f.readlines())
        parsed = parse_lines(lines)
        tokens = itertools.chain(*(line.tokens() for line in parsed))
        assert_that(tokenize.untokenize(tokens), is_(''.join(lines)))

    def test_parse_line_children_roundtrip(self):
        with open(in_path('to_parse.py')) as f:
            lines = list(f.readlines())
        parsed = parse_lines(lines)
        tokens = itertools.chain.from_iterable(line.children for line in parsed)
        assert_that(tokenize.untokenize(tokens), is_(''.join(lines)))

    def test_token_roundtrip(self):
        with open(__file__) as f:
            file_str = ''.join(f.readlines())
        with open(__file__) as f:
            a = list(tokenize.generate_tokens(f.readline))
            assert_that(tokenize.untokenize(a), is_(file_str))
