import unittest

from hamcrest import assert_that, is_

from tests.sample.dict import dict


class TestInstanceMethod(unittest.TestCase):
    def test_some_method(self):
        assert_that(dict.some_method({1: '2'}), is_({1: '2'}))
