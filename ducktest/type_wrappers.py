import types
from abc import abstractmethod, ABCMeta
from collections import namedtuple, Container, Iterable, Mapping, defaultdict, OrderedDict

import mock
from future.utils import iteritems
from past.builtins import basestring

CO_GENERATOR = 0x20


def is_generator(frame):
    return frame.f_code.co_flags & CO_GENERATOR != 0


def get_first_line_number(frame):
    return frame.f_code.co_firstlineno


def get_function_name(frame):
    return frame.f_code.co_name


def get_file_name(frame):
    return frame.f_code.co_filename


def get_variable_names(frame):
    return frame.f_code.co_varnames


def get_local_variable(frame, variable_name):
    return frame.f_locals[variable_name]


class Processor(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.next_processor = None

    @abstractmethod
    def process(self, *args, **kwargs):
        pass


def last_after(processor):
    while processor.next_processor:
        processor = processor.next_processor
    return processor


def chain(*processors):
    for first, second in zip(processors[:-1], processors[1:]):
        last_after(first).next_processor = second
    return processors[0]


class DirectoriesValidater(Processor):
    def __init__(self, included_directories):
        super(DirectoriesValidater, self).__init__()
        self.included_directories = included_directories

    def process(self, frame, *args):
        for included_directory in self.included_directories:
            if get_file_name(frame).startswith(included_directory):
                self.next_processor.process(frame, *args)


class CallVariableSplitter(Processor):
    def process(self, frame):
        for name in get_variable_names(frame):
            try:
                value = get_local_variable(frame, name)
            except KeyError:
                continue
            self.next_processor.process(value, name, frame)


class ReturnVariableSplitter(Processor):
    def process(self, frame, return_value):
        self.next_processor.process(return_value, frame)


class NameValidater(Processor):
    def __init__(self, excluded_names):
        super(NameValidater, self).__init__()
        self.excluded_names = excluded_names

    def process(self, value, name, frame):
        if name not in self.excluded_names:
            self.next_processor.process(value, name, frame)


PlainTypeWrapper = namedtuple('PlainTypeWrapper', 'own_type')
ContainerTypeWrapper = namedtuple('ContainerTypeWrapper', ['own_type', 'contained_types'])
MappingTypeWrapper = namedtuple('MappingTypeWrapper', ['own_type', 'mapped_types'])


def get_plain_type(parameter):
    if isinstance(parameter, mock.Mock):
        if parameter._spec_class:
            return parameter._spec_class
        else:
            raise ValueError('Mock without _spec_class used')
    else:
        return type(parameter)


class ConditionalTypeProcessor(Processor):
    __metaclass__ = ABCMeta

    def process(self, *args, **kwargs):
        if self._condition(*args, **kwargs):
            try:
                return frozenset([self._process(*args, **kwargs)])
            except ValueError:
                return frozenset()
        else:
            return self.next_processor.process(*args, **kwargs)

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
        own_type = get_plain_type(mapping)
        mapped_types = set()
        for key, value in iteritems(mapping):
            try:
                mapped_types.add((self._get_type(key), self._get_type(value)))
            except ValueError:
                pass
        if mapped_types:
            return MappingTypeWrapper(own_type, frozenset(mapped_types))
        return PlainTypeWrapper(own_type)


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
        own_type = get_plain_type(container)
        contained_types = set()
        for contained in container:
            try:
                contained_types.update(self._get_type(contained))
            except ValueError:
                continue
        if contained_types:
            return ContainerTypeWrapper(own_type, frozenset(contained_types))
        return PlainTypeWrapper(own_type)


class PlainTypeProcessor(Processor):
    def process(self, value):
        """implicit end of chain"""
        try:
            return frozenset({PlainTypeWrapper(get_plain_type(value))})
        except ValueError:
            return frozenset()


class GeneratorTypeProcessor(Processor):
    def __init__(self, return_types):
        super(GeneratorTypeProcessor, self).__init__()
        self.return_types = return_types

    def process(self, return_value, frame):
        if is_generator(frame):
            self.return_types.store({PlainTypeWrapper(types.GeneratorType)}, frame)
        else:
            self.next_processor.process(return_value, frame)


class IdleProcessor(Processor):
    def process(self, *args, **kwargs):
        return self.next_processor.process(*args, **kwargs)


class CallTypeStorer(Processor):
    def __init__(self, call_types, processor):
        super(CallTypeStorer, self).__init__()
        self.get_type = processor.process
        self.call_types = call_types

    def process(self, value, name, frame):
        self.call_types.store(self.get_type(value), name, frame)


class ReturnTypeStorer(Processor):
    def __init__(self, return_types, processor):
        super(ReturnTypeStorer, self).__init__()
        self.get_type = processor.process
        self.return_types = return_types

    def process(self, value, frame):
        if not value is None:
            self.return_types.store(self.get_type(value), frame)


FunctionParameters = namedtuple('FunctionParameters', ['line_number', 'types'])


class OrderedDefaultDict(OrderedDict):
    def __init__(self, default_factory, *args, **kwds):
        super(OrderedDefaultDict, self).__init__(*args, **kwds)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            value = self.default_factory()
            self[key] = value
            return value


class CallTypesRepository(object):
    def __init__(self):
        self._dict = defaultdict(lambda: defaultdict(lambda: (OrderedDefaultDict(set))))

    def store(self, a_type, name, frame):
        self._dict[get_file_name(frame)][get_first_line_number(frame)][name].update(a_type)

    def file_names(self):
        return set(self._dict.keys())

    def line_numbers(self, file_name):
        return self._dict[file_name].keys()

    def call_types(self, file_name, line_number):
        return self._dict[file_name][line_number]

    def sorted_call_types(self, file_name):
        findings_in_file = self._dict[file_name]
        line_numbers = sorted(findings_in_file.keys(), reverse=True)
        return [FunctionParameters(line_number, findings_in_file[line_number]) for line_number in line_numbers]


class ReturnTypesRepository(object):
    def __init__(self):
        self._dict = defaultdict(lambda: defaultdict(set))

    def store(self, a_type, frame):
        self._dict[get_file_name(frame)][get_first_line_number(frame)].update(a_type)

    def file_names(self):
        return set(self._dict.keys())

    def return_types(self, file_name, line_number):
        return self._dict[file_name][line_number]

    def sorted_return_types(self, file_name):
        findings_in_file = self._dict[file_name]
        line_numbers = sorted(findings_in_file.keys(), reverse=True)
        return [FunctionParameters(line_number, findings_in_file[line_number]) for line_number in line_numbers]


class FrameProcessors(object):
    def __init__(self, configuration):
        """:type configuration: ducktest.config_reader.Configuration"""
        self.call_types = CallTypesRepository()
        self.return_types = ReturnTypesRepository()

        head = IdleProcessor()
        typer = chain(
            head,
            MappingTypeProcessor(head),
            ContainerTypeProcessor(head),
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
            GeneratorTypeProcessor(self.return_types),
            ReturnTypeStorer(self.return_types, typer),
        )
