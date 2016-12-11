import unittest

from hamcrest import assert_that, is_
from os import path

from ducktest.sphinx_docstring import read_file, parse_docstrings


class TestParser(unittest.TestCase):
    def test_some(self):
        here = path.abspath(path.dirname(__file__))
        lines = read_file(path.join(here, 'parse_example.py'))
        positions = parse_docstrings(lines)

        assert_that(positions, is_({
            5: (6, 8, 6, 14, ['""""""']), 9: (10, 8, 10, 8, []), 12: (14, 8, 14, 23, ['"""one liner"""']),
            17: (18, 8, 19, 16, ['"""two', 'liner"""']), 21: (22, 8, 24, 11, ['"""', 'three liner', '"""']),
            26: (27, 8, 27, 47, ['"""with newline \\n, or at the end \\n"""'])
        }))
