from abc import abstractmethod, ABCMeta
from collections import namedtuple, Container, Iterable, Mapping

import mock
from future.utils import iteritems

from ducktest.another_typer import Processor, CallTypesRepository, ReturnTypesRepository, chain, DirectoriesValidater, \
    CallVariableSplitter, NameValidater, ReturnVariableSplitter, get_file_name, get_first_line_number

PlainTypeWrapper = namedtuple('PlainTypeWrapper', 'own_type')
ContainerTypeWrapper = namedtuple('ContainerTypeWrapper', ['own_type', 'contained_types'])
MappingTypeWrapper = namedtuple('MappingTypeWrapper', ['own_type', 'mapped_types'])


def get_plain_type(parameter):
    if isinstance(parameter, mock.Mock):
        try:
            return parameter._spec_class
        except AttributeError:
            raise ValueError('Mock without _spec_class used')
    else:
        return type(parameter)


class ConditionalTypeProcessor(Processor):
    __metaclass__ = ABCMeta

    def process(self, *args, **kwargs):
        if self._condition(*args, **kwargs):
            try:
                return frozenset({self._process(*args, **kwargs)})
            except ValueError:
                return set()
        else:
            self.next_processor.process(*args, **kwargs)

    @abstractmethod
    def _condition(self, *args, **kwargs):
        pass

    @abstractmethod
    def _process(self, *args, **kwargs):
        pass


class MappingTypeProcessor(ConditionalTypeProcessor):
    def __init__(self, head):
        super(MappingTypeProcessor, self).__init__()
        self._get_type = head.process

    def _condition(self, mapping):
        return isinstance(mapping, Mapping)

    def _process(self, mapping):
        mapped_types = set()
        for key, value in iteritems(mapping):
            try:
                mapped_types.add((self._get_type(key), self._get_type(value)))
            except ValueError:
                pass
        return MappingTypeWrapper(get_plain_type(mapping), mapped_types)


class ContainerTypeProcessor(ConditionalTypeProcessor):
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
        contained_types = set()
        for contained in container:
            try:
                contained_types.add(self._get_type(contained))
            except ValueError:
                continue
        return ContainerTypeWrapper(get_plain_type(container), contained_types)


class PlainTypeProcessor(Processor):
    def process(self, value):
        """implicit end of chain"""
        return {PlainTypeWrapper(get_plain_type(value))}


class IdleProcessor(Processor):
    def process(self, *args, **kwargs):
        self.next_processor.process(*args, **kwargs)


class CallTypeStorer(Processor):
    def __init__(self, call_types, processor):
        super(CallTypeStorer, self).__init__()
        self.get_type = processor.process
        self.call_types = call_types

    def process(self, value, name, frame):
        function_dict, parameter_order = self.call_types._dict[get_file_name(frame)][get_first_line_number(frame)]
        if name not in function_dict.keys():
            parameter_order.append(name)
        function_dict[name] += self.get_type(value)


class ReturnTypeStorer(Processor):
    def __init__(self, return_types, processor):
        super(ReturnTypeStorer, self).__init__()
        self.get_type = processor.process
        self.return_types = return_types

    def process(self, value, name, frame):
        self.return_types._dict[get_file_name(frame)][get_first_line_number(frame)] += self.get_type(value)


class FrameProcessors(object):
    def __init__(self, configuration):
        """:type configuration: ducktest.config_reader.Configuration"""
        self.call_types = CallTypesRepository()
        self.return_types = ReturnTypesRepository()

        call_head = IdleProcessor()
        typer = chain(
            call_head,
            MappingTypeProcessor(call_head),
            ContainerTypeProcessor(call_head),
            PlainTypeProcessor()
        )

        self.call_frame_processor = chain(
            DirectoriesValidater(configuration.write_docstrings_in_directories),
            CallVariableSplitter(),
            NameValidater(configuration.ignore_call_parameter_names),
            CallTypeStorer(self.call_types, typer)
        )

        self.return_frame_processor = chain(
            DirectoriesValidater(configuration.write_docstrings_in_directories),
            ReturnVariableSplitter(),
            ReturnTypeStorer(self.return_types, typer),
        )