import unittest

from hamcrest import assert_that, is_
from mock import create_autospec

from tests.sample.autospec.autospec import SomeClassToAutospec, use_autospec


class TestSomeAutospec(unittest.TestCase):
    def test_some_autospec(self):
        a = create_autospec(SomeClassToAutospec)
        assert_that(use_autospec(a), is_('not'))
