"""
Copyright 2016 Markus Wissinger. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import threading
import types
from abc import abstractmethod, ABCMeta
from collections import Container, Iterable, Mapping, defaultdict, OrderedDict

import mock
import six
from future.utils import iteritems

from ducktest.base import PlainTypeWrapper, ContainerTypeWrapper, MappingTypeWrapper, Processor, chain
from ducktest.subtypes import remove_subtypes

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


class DirectoriesValidater(Processor):
    def __init__(self, included_directories):
        super(DirectoriesValidater, self).__init__()
        self.included_directories = included_directories

    def process(self, frame, *args):
        for included_directory in self.included_directories:
            if get_file_name(frame).startswith(included_directory):
                self.next_processor.process(frame, *args)


class CallVariableSplitter(Processor):
    def __init__(self):
        super(CallVariableSplitter, self).__init__()
        self.known = {}

    def process(self, frame):
        key = get_file_name(frame), get_function_name(frame), get_first_line_number(frame)
        names = self.known.get(key)
        if names is None:
            names = tuple(name for name in get_variable_names(frame) if name in frame.f_locals)
            self.known[key] = names
        for name in names:
            try:
                value = get_local_variable(frame, name)
                self.next_processor.process(value, name, frame)
            except KeyError:
                pass


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
                continue
        return MappingTypeWrapper(own_type, frozenset(mapped_types))


class ContainerTypeProcessor(ConditionalTypeProcessor):
    def __init__(self, head):
        super(ContainerTypeProcessor, self).__init__()
        self._get_type = head.process

    def _condition(self, container):
        return all([
            isinstance(container, Container),
            isinstance(container, Iterable),
            not isinstance(container, six.string_types),
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
        return ContainerTypeWrapper(own_type, frozenset(contained_types))


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

    def process(self, frame, return_value):
        if is_generator(frame):
            self.return_types.store({PlainTypeWrapper(types.GeneratorType)}, frame)
        else:
            self.next_processor.process(frame, return_value)


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

    def process(self, frame, value):
        if not value is None:
            self.return_types.store(self.get_type(value), frame)


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
    lock = threading.Lock()

    def __init__(self):
        self._dict = defaultdict(lambda: defaultdict(lambda: (OrderedDefaultDict(set))))

    def store(self, a_type, name, frame):
        with self.lock:
            self._dict[get_file_name(frame)][get_first_line_number(frame)][name].update(a_type)

    def call_types(self, file_name, line_number):
        calltypes = self._dict[file_name][line_number]
        result = OrderedDict()
        for name, value in iteritems(calltypes):
            result[name] = remove_subtypes(value)
        return result


class ReturnTypesRepository(object):
    lock = threading.Lock()

    def __init__(self):
        self._dict = defaultdict(lambda: defaultdict(set))

    def store(self, a_type, frame):
        with self.lock:
            self._dict[get_file_name(frame)][get_first_line_number(frame)].update(a_type)

    def return_types(self, file_name, line_number):
        returntypes = self._dict[file_name][line_number]
        result = remove_subtypes(returntypes)
        return result


def frame_processors(configuration, call_types, return_types):
    """:type configuration: ducktest.config_reader.Configuration"""
    typer = IdleProcessor()
    chain(
        typer,
        MappingTypeProcessor(typer),
        ContainerTypeProcessor(typer),
        PlainTypeProcessor(),
    )

    call_frame_processor = chain(
        DirectoriesValidater(configuration.write_docstrings_in_directories),
        CallVariableSplitter(),
        CallTypeStorer(call_types, typer)
    )

    return_frame_processor = chain(
        DirectoriesValidater(configuration.write_docstrings_in_directories),
        GeneratorTypeProcessor(return_types),
        ReturnTypeStorer(return_types, typer),
    )

    return call_frame_processor, return_frame_processor


class Tracer(object):
    def __init__(self, top_level_dir, call_frame_processor, return_frame_processor):
        self.top_level_dir = top_level_dir
        self.on_call = call_frame_processor.process
        self.on_return = return_frame_processor.process

    def runcall(self, method, *args, **kwargs):
        sys.settrace(self.trace_dispatch)
        result = method(*args, **kwargs)
        sys.settrace(None)
        return result

    def trace_dispatch(self, frame, event, arg):
        if get_file_name(frame).startswith(self.top_level_dir):
            if event == 'call':
                self.on_call(frame)
            elif event == 'return':
                self.on_return(frame, arg)
        return self.trace_dispatch
