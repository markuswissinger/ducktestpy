import unittest

from hamcrest import assert_that, is_

from tests.sample.integration.integration import multi_line_docstring_example


class TestIntegration(unittest.TestCase):
    def test_multiline_docstring(self):
        assert_that(multi_line_docstring_example(), is_('Eric the half a bee'))