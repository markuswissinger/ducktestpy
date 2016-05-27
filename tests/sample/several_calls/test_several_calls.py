import unittest

from hamcrest import assert_that, is_

from tests.sample.several_calls.several_calls import call_me_several_times


class TestSeveralCalls(unittest.TestCase):
    def test_a_call(self):
        assert_that(call_me_several_times(1), is_(1))

    def test_another_call(self):
        assert_that(call_me_several_times(2), is_(2))
