import unittest

from hamcrest import assert_that, is_
from mock import Mock

from tests.sample.function import function


class TestInstanceMethod(unittest.TestCase):
    def test_a_function(self):
        assert_that(function.a_method(function.some_method), is_('hui'))

    def test_a_mocked_function(self):
        f = Mock(return_value=1)
        assert_that(function.b_method(f), is_(1))
