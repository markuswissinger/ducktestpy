from abc import abstractmethod, ABCMeta
from collections import namedtuple, Container, Iterable, Mapping

import mock
from future.utils import iteritems

from ducktest.another_typer import Processor


def get_plain_type(parameter):
    if isinstance(parameter, mock.Mock):
        try:
            return parameter._spec_class
        except AttributeError:
            raise ValueError('Mock has no _spec_class')
    else:
        return type(parameter)


PlainTypeWrapper = namedtuple('PlainTypeWrapper', 'own_type')
ContainerTypeWrapper = namedtuple('ContainerTypeWrapper', ['own_type', 'contained_types'])
MappingTypeWrapper = namedtuple('MappingTypeWrapper', ['own_type', 'mapped_types'])


class ConditionalProcessor(Processor):
    __metaclass__ = ABCMeta

    def process(self, *args, **kwargs):
        if self._condition(*args, **kwargs):
            self._process(*args, **kwargs)
        else:
            self.next_processor.process(*args, **kwargs)

    @abstractmethod
    def _condition(self, *args, **kwargs):
        pass

    @abstractmethod
    def _process(self, *args, **kwargs):
        pass


class MappingTypeProcessor(ConditionalProcessor):
    def __init__(self, head):
        super(MappingTypeProcessor, self).__init__()
        self._get_type = head.process

    def _process(self, mapping):
        mapped_types = set([(self._get_type(key), self._get_type(value)) for key, value in iteritems(mapping)])
        return MappingTypeWrapper(get_plain_type(mapping), mapped_types)


class ContainerTypeProcessor(ConditionalProcessor):
    def __init__(self, head):
        super(ContainerTypeProcessor, self).__init__()
        self._get_type = head.process

    def _condition(self, container):
        return all([
            isinstance(container, Container),
            isinstance(container, Iterable),
            not isinstance(container, basestring),
            not isinstance(container, Mapping)
        ])

    def _process(self, container):
        contained_types = set([self._get_type(contained_types) for contained_types in container])
        return ContainerTypeWrapper(get_plain_type(container), contained_types)


class PlainTypeProcessor(Processor):
    def process(self, value):
        """implicit end of chain"""
        return PlainTypeWrapper(get_plain_type(value))
