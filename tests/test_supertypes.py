import unittest
from collections import Iterable, OrderedDict

from hamcrest import assert_that, is_

from ducktest.base import PlainTypeWrapper, ContainerTypeWrapper, MappingTypeWrapper
from ducktest.subtypes import is_subtype, remove_subtypes


class A(object):
    pass


class B(A):
    pass


PLAIN_A = PlainTypeWrapper(A)
PLAIN_B = PlainTypeWrapper(B)
PLAIN_INT = PlainTypeWrapper(int)

LIST_A = ContainerTypeWrapper(list, frozenset([PLAIN_A]))
LIST_B = ContainerTypeWrapper(list, frozenset([PLAIN_B]))

EMPTY_LIST = ContainerTypeWrapper(list, frozenset())

LIST_LIST_A = ContainerTypeWrapper(list, frozenset([LIST_A]))
LIST_LIST_B = ContainerTypeWrapper(list, frozenset([LIST_B]))

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
        assert not is_subtype(ITERABLE_A, LIST_B)

    def test_different_own_type(self):
        assert is_subtype(LIST_A, ITERABLE_A)
        assert not is_subtype(ITERABLE_A, LIST_A)


DICT = MappingTypeWrapper(dict, frozenset())
ORDERED_DICT = MappingTypeWrapper(OrderedDict, frozenset())


def get_mapping_wrapper_b(own, key, value):
    return MappingTypeWrapper(own, frozenset([(frozenset([key]), frozenset([value]))]))


def get_mapping_wrapper(own, keys, values):
    return MappingTypeWrapper(own, frozenset([(frozenset(keys), frozenset(values))]))


MAP_A_INT = get_mapping_wrapper(dict, [PLAIN_A], [PLAIN_INT])
MAP_B_INT = get_mapping_wrapper(dict, [PLAIN_B], [PLAIN_INT])

MAP_INT_A = get_mapping_wrapper(dict, [PLAIN_INT], [PLAIN_A])
MAP_INT_B = get_mapping_wrapper(dict, [PLAIN_INT], [PLAIN_B])


class C(object):
    pass


class D(C):
    pass


PLAIN_C = PlainTypeWrapper(C)
PLAIN_D = PlainTypeWrapper(D)

MAP_A_C = get_mapping_wrapper(dict, [PLAIN_A], [PLAIN_C])
MAP_B_D = get_mapping_wrapper(dict, [PLAIN_B], [PLAIN_D])

MULTI_MAP_AC = get_mapping_wrapper(dict, [PLAIN_A, PLAIN_C], [PLAIN_INT])
MULTI_MAP_BC = get_mapping_wrapper(dict, [PLAIN_B, PLAIN_C], [PLAIN_INT])

MULTI_MAP_ACC = get_mapping_wrapper(dict, [PLAIN_A, PLAIN_C], [PLAIN_C])


class TestIsSubtypeMappings(unittest.TestCase):
    def test_own_type(self):
        assert is_subtype(ORDERED_DICT, DICT)
        assert not is_subtype(DICT, ORDERED_DICT)

    def test_key_type(self):
        assert is_subtype(MAP_B_INT, MAP_A_INT)
        assert not is_subtype(MAP_A_INT, MAP_B_INT)

    def test_value_type(self):
        assert is_subtype(MAP_INT_B, MAP_INT_A)
        assert not is_subtype(MAP_INT_A, MAP_INT_B)

    def test_key_value(self):
        assert is_subtype(MAP_B_D, MAP_A_C)
        assert not is_subtype(MAP_A_C, MAP_B_D)

    def test_empty(self):
        assert is_subtype(DICT, MAP_A_C)
        assert not is_subtype(MAP_A_C, DICT)

    def test_multi_map(self):
        assert is_subtype(MULTI_MAP_BC, MULTI_MAP_AC)
        assert not is_subtype(MULTI_MAP_AC, MULTI_MAP_BC)

    def test_another_multimap(self):
        assert is_subtype(MAP_A_C, MULTI_MAP_ACC)
        assert not is_subtype(MULTI_MAP_ACC, MAP_A_C)


class TestRemoveSubtypes(unittest.TestCase):
    def test_remove(self):
        wrappers = {MAP_A_INT, MAP_B_INT}
        assert_that(remove_subtypes(wrappers), is_({MAP_A_INT}))

    def test_real(self):
        wrappers = {
            MappingTypeWrapper(dict, frozenset([
                (frozenset([PlainTypeWrapper(int)]), frozenset([PlainTypeWrapper(A)]))
            ])),
            MappingTypeWrapper(dict, frozenset([
                (frozenset([PlainTypeWrapper(int)]), frozenset([PlainTypeWrapper(B)]))
            ])),
        }
        assert_that(remove_subtypes(wrappers), is_({
            MappingTypeWrapper(dict, frozenset([
                (frozenset([PlainTypeWrapper(int)]), frozenset([PlainTypeWrapper(A)]))
            ])),
        }))
