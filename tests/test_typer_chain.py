import unittest

from hamcrest import assert_that, is_

from ducktest.type_wrappers import IdleProcessor, MappingTypeProcessor, ContainerTypeProcessor, PlainTypeProcessor, \
    PlainTypeWrapper, ContainerTypeWrapper, MappingTypeWrapper, chain


class TestTyperChain(unittest.TestCase):
    def setUp(self):
        head = IdleProcessor()
        typer = chain(
            head,
            MappingTypeProcessor(head),
            ContainerTypeProcessor(head),
            PlainTypeProcessor()
        )
        self.get_type = typer.process

    def test_plain(self):
        assert_that(self.get_type(1), is_({PlainTypeWrapper(type(1))}))

    def test_list(self):
        assert_that(self.get_type([1]), is_({ContainerTypeWrapper(type([]), frozenset([PlainTypeWrapper(type(1))]))}))

    def test_dict(self):
        expected = {MappingTypeWrapper(type({1: '2'}),
                                       frozenset([(frozenset([PlainTypeWrapper(type(1))]),
                                                   frozenset([PlainTypeWrapper(type('2'))]))]))}
        assert_that(self.get_type({1: '2'}), is_(expected))

    def test_list_of_list(self):
        assert_that(self.get_type([[1]]), is_({ContainerTypeWrapper(type([]), frozenset(
            [ContainerTypeWrapper(type([]), frozenset([PlainTypeWrapper(type(1))]))]))}))

    def test_dict_of_dict(self):
        assert_that(self.get_type({1: {'2': u'3'}}), is_(frozenset([MappingTypeWrapper(type({}), frozenset([(frozenset(
            [PlainTypeWrapper(type(1))]), frozenset([MappingTypeWrapper(type({}), frozenset(
            [(frozenset([PlainTypeWrapper(type('2'))]), frozenset([PlainTypeWrapper(type(u''))]))]))]))]))])))
