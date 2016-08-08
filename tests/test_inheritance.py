import unittest

from hamcrest import assert_that, is_

from ducktest.inheritance import handle_plain
from ducktest.type_wrappers import PlainTypeWrapper


class Sup(object):
    pass


class Sub(Sup):
    pass


class TestInheritanceResolution(unittest.TestCase):
    def test_plain(self):
        edukt = {PlainTypeWrapper(int), PlainTypeWrapper(Sup), PlainTypeWrapper(Sub)}
        assert_that(handle_plain(edukt), is_({PlainTypeWrapper(int), PlainTypeWrapper(Sup)}))
