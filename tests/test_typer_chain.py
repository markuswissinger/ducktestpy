import unittest

from hamcrest import assert_that, is_

from ducktest.another_typer import chain
from ducktest.type_wrappers import IdleProcessor, MappingTypeProcessor, ContainerTypeProcessor, PlainTypeProcessor, \
    PlainTypeWrapper, ContainerTypeWrapper, MappingTypeWrapper


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
        expected = {MappingTypeWrapper(type({1: 2}),
                                       frozenset([(frozenset([PlainTypeWrapper(type(1))]),
                                                   frozenset([PlainTypeWrapper(type(2))]))]))}
        assert_that(self.get_type({1: 2}), is_(expected))
