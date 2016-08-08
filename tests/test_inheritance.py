import unittest
from collections import Container

from hamcrest import assert_that, is_

from ducktest.inheritance import handle_plain, handle_container
from ducktest.type_wrappers import PlainTypeWrapper, ContainerTypeWrapper


class Sup(object):
    pass


class Sub(Sup):
    pass


class TestInheritanceResolution(unittest.TestCase):
    def test_plain(self):
        edukt = {PlainTypeWrapper(int), PlainTypeWrapper(Sup), PlainTypeWrapper(Sub)}
        assert_that(handle_plain(edukt), is_({PlainTypeWrapper(int), PlainTypeWrapper(Sup)}))

    def test_container(self):
        wrappers = {ContainerTypeWrapper(list, frozenset({PlainTypeWrapper(int)}))}
        handle_container(wrappers)
        assert_that(wrappers, is_({ContainerTypeWrapper(list, frozenset({PlainTypeWrapper(int)}))}))
