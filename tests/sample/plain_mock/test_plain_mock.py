import unittest

import mock
from hamcrest import assert_that, is_

from tests.sample.plain_mock import plain_mock


class TestPlainMock(unittest.TestCase):
    def test_one(self):
        a = mock.Mock()
        assert_that(plain_mock.some_method(a), is_(a))

    def test_two(self):
        b = mock.Mock()
        assert_that(plain_mock.some_method(b), is_(b))

    def test_three(self):
        assert_that(plain_mock.some_method(1), is_(1))
