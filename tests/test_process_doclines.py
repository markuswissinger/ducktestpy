import unittest

from hamcrest import assert_that, is_

from ducktest.sphinx_docstring import process_doclines


class TestProcessDocLines(unittest.TestCase):
    def test_some(self):
        assert_that(process_doclines(['"""hui"""']), is_((['hui'], '"""')))

    def test_more_lines(self):
        assert_that(process_doclines(['"""', 'hui', '"""']), is_((['hui'], '"""')))

    def test_another(self):
        assert_that(process_doclines(['"""', "'hui'", '"""']), is_((["'hui'"], '"""')))

    def test_yet_another(self):
        assert_that(process_doclines(['"""', "'", "'", '"""']), is_((["'", "'"], '"""')))
