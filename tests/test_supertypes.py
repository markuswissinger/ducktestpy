import unittest
from collections import Iterable

from ducktest.base import PlainTypeWrapper, ContainerTypeWrapper
from ducktest.supertypes import is_subtype


class A(object):
    pass


class B(A):
    pass


PLAIN_A = PlainTypeWrapper(A)
PLAIN_B = PlainTypeWrapper(B)

LIST_A = ContainerTypeWrapper(type([]), frozenset([PLAIN_A]))
LIST_B = ContainerTypeWrapper(type([]), frozenset([PLAIN_B]))

EMPTY_LIST = ContainerTypeWrapper(type([]), frozenset())

LIST_LIST_A = ContainerTypeWrapper(type([]), frozenset([LIST_A]))
LIST_LIST_B = ContainerTypeWrapper(type([]), frozenset([LIST_B]))

ITERABLE_A = ContainerTypeWrapper(Iterable, frozenset([PLAIN_A]))


class TestIsSubtype(unittest.TestCase):
    def test_plain(self):
        assert is_subtype(PLAIN_B, PLAIN_A)
        assert not is_subtype(PLAIN_A, PLAIN_B)

    def test_list(self):
        assert is_subtype(LIST_B, LIST_A)
        assert not is_subtype(LIST_A, LIST_B)

    def test_empty_list(self):
        assert is_subtype(EMPTY_LIST, LIST_A)  # is this really correct?
        assert is_subtype(EMPTY_LIST, LIST_LIST_A)

    def test_list_and_list_list(self):
        assert not is_subtype(LIST_A, LIST_LIST_A)
        assert not is_subtype(LIST_LIST_A, LIST_A)

    def test_list_list(self):
        assert is_subtype(LIST_LIST_B, LIST_LIST_A)
        assert not is_subtype(LIST_LIST_A, LIST_LIST_B)

    def test_different_own_type_and_contained(self):
        assert is_subtype(LIST_B, ITERABLE_A)

    def test_different_own_type(self):
        assert is_subtype(LIST_A, ITERABLE_A)
