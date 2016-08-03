import unittest

from hamcrest import assert_that, is_

from tests.sample.integration.integration import multi_line_docstring_example, no_docstring, new_docstring, \
    single_line_docstring, two_line_docstring


class TestIntegration(unittest.TestCase):
    def test_multiline_docstring(self):
        assert_that(multi_line_docstring_example(), is_('Eric the half a bee'))

    def test_no_docstring(self):
        assert_that(no_docstring(), is_(None))

    def test_new_docstring(self):
        assert_that(new_docstring('a'), is_('a'))

    def test_single_line_docstring(self):
        assert_that(single_line_docstring('a'), is_('a'))

    def test_two_line_docstring(self):
        assert_that(two_line_docstring(), is_(1))