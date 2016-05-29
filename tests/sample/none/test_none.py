import unittest

from hamcrest import assert_that, is_

from tests.sample.none import none


class TestNone(unittest.TestCase):
    def test_none(self):
        assert_that(none.some_method(None), is_(None))
