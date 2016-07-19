import unittest

from hamcrest import assert_that, is_

from ducktest.docstring_parser import read_file, parse_docstrings


class TestParser(unittest.TestCase):
    def test_some(self):
        lines = read_file('parse_example.py')
        positions = parse_docstrings(lines)

        assert_that(positions, is_({
            5: (5, 8, 5, 14, []),
            9: (9, 8, 9, 8, ''),
            12: (13, 8, 13, 23, ['one liner']),
            17: (17, 8, 18, 16, ['two', 'liner']),
            21: (21, 8, 23, 11, ['three liner']),
            26: (26, 8, 26, 47, ['with newline \\n, or at the end \\n'])
        }))
