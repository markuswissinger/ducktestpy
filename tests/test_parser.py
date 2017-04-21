import os
import sys
import tokenize
import unittest

from hamcrest import assert_that, is_

from ducktest.parser import parse_lines, parse_blocks

python_major = int(sys.version.split('.')[0])

path = os.path.split(__file__)[0]


def in_path(a_file):
    return os.path.join(path, a_file)


class TestParser(unittest.TestCase):
    def test_parse(self):
        if python_major > 2:
            return

        with open(in_path('to_parse.py')) as f:
            lines = f.readlines()
            parsed = parse_lines(lines)
            root_block = parse_blocks(parsed)
            line_0_tokens = [
                (1, 'class', (1, 0), (1, 5), 'class Some(object):\n'),
                (1, 'Some', (1, 6), (1, 10), 'class Some(object):\n'),
                (51, '(', (1, 10), (1, 11), 'class Some(object):\n'),
                (1, 'object', (1, 11), (1, 17), 'class Some(object):\n'),
                (51, ')', (1, 17), (1, 18), 'class Some(object):\n'),
                (51, ':', (1, 18), (1, 19), 'class Some(object):\n'),
                (4, '\n', (1, 19), (1, 20), 'class Some(object):\n'),
            ]
            assert_that(root_block.children[0].children[0].children, is_(line_0_tokens))
            assert_that(root_block.children[0].children[0].name, is_('Some'))

            line_1_tokens = [
                (1, 'def', (2, 4), (2, 7), '    def __init__(self, a):\n'),
                (1, '__init__', (2, 8), (2, 16), '    def __init__(self, a):\n'),
                (51, '(', (2, 16), (2, 17), '    def __init__(self, a):\n'),
                (1, 'self', (2, 17), (2, 21), '    def __init__(self, a):\n'),
                (51, ',', (2, 21), (2, 22), '    def __init__(self, a):\n'),
                (1, 'a', (2, 23), (2, 24), '    def __init__(self, a):\n'),
                (51, ')', (2, 24), (2, 25), '    def __init__(self, a):\n'),
                (51, ':', (2, 25), (2, 26), '    def __init__(self, a):\n'),
                (4, '\n', (2, 26), (2, 27), '    def __init__(self, a):\n'),
            ]
            assert_that(root_block.children[0].children[1].children[0].children, is_(line_1_tokens))
            assert_that(root_block.children[0].children[1].children[0].name, is_('__init__'))

            assert_that(root_block.children[0].children[1].children[1].children, is_([
                (3, '"""a docstring"""', (3, 8), (3, 25), '        """a docstring"""\n'),
                (4, '\n', (3, 25), (3, 26), '        """a docstring"""\n'),
            ]))

    def test_round_trip(self):
        with open(in_path('to_parse.py')) as f:
            lines = f.readlines()
            parsed = parse_lines(lines)
            root_block = parse_blocks(parsed)
            assert_that(tokenize.untokenize(root_block.tokens()), is_(''.join(lines)))

    def test_parseB(self):
        with open(in_path('to_parse.py')) as f:
            lines = f.readlines()
            parsed = parse_lines(lines)
            root_block = parse_blocks(parsed)
            print('ui')
