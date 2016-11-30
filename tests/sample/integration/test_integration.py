import unittest

from hamcrest import assert_that, is_
from mock import Mock, create_autospec

from tests.sample.integration.integration import multi_line_docstring_example, no_docstring, new_docstring, \
    single_line_docstring, two_line_docstring, list_example, single_result_line, mock_example, non_builtin_example, \
    generator_example
from tests.sample.integration.stuff import Some, Other


class TestIntegration(unittest.TestCase):
    def test_multiline_docstring(self):
        assert_that(multi_line_docstring_example(), is_('Eric the half a bee'))

    def test_no_docstring(self):
        assert_that(no_docstring(), is_(None))

    def test_new_docstring(self):
        assert_that(new_docstring('a'), is_('a'))

    def test_single_result_line(self):
        assert_that(single_result_line(), is_(1))

    def test_single_line_docstring(self):
        assert_that(single_line_docstring('a'), is_('a'))

    def test_two_line_docstring(self):
        assert_that(two_line_docstring(), is_(1))

    def test_list_example(self):
        assert_that(list_example([]), is_([]))
        assert_that(list_example([1, "1"]), is_([1, "1"]))

    def test_mock_example(self):
        a = Mock()
        b = create_autospec(int)
        c = create_autospec(Some)
        assert_that(mock_example(a), is_(a))
        assert_that(mock_example(b), is_(b))
        assert_that(mock_example(c), is_(c))

    def test_non_builtin(self):
        some = Some()
        other = Other()
        assert_that(non_builtin_example(some), is_(some))
        assert_that(non_builtin_example(other), is_(other))

    def test_generator(self):
        a = [number for number in generator_example()]
        assert_that(a, is_([1]))
