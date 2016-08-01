import unittest

from hamcrest import assert_that, is_

from tests.sample.integration.integration import multi_line_docstring_example, no_docstring, new_docstring


class TestIntegration(unittest.TestCase):
    def test_multiline_docstring(self):
        assert_that(multi_line_docstring_example(), is_('Eric the half a bee'))

    def test_no_docstring(self):
        assert_that(no_docstring(), is_(None))

    def test_new_docstring(self):
        assert_that(new_docstring('a'), is_('a'))