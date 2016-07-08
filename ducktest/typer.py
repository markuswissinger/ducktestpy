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

import collections
import types
import unittest
from collections import defaultdict
import sys

from future.utils import iteritems
from mock import Mock
from past.builtins import basestring
from builtins import object

CO_GENERATOR = 0x20
CO_VARARGS = 0x04
CO_KWARGS = 0x08


def has_varargs(frame):
    return frame.f_code.co_flags & CO_VARARGS != 0


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


def get_docstring(frame):
    try:
        return frame.f_code.co_consts[0]
    except IndexError:
        return None


class TypeWrapper(object):
    def __init__(self, parameter, generator=False):
        self.is_generator = generator
        self.type = self.get_type(parameter)
        self.contained_types = self.get_contained_types(parameter)
        self.mapped_types = self.get_mapped_types(parameter)

    def get_type(self, parameter):
        if self.is_generator:
            return types.GeneratorType
        if isinstance(parameter, Mock):
            if parameter._spec_class:
                return parameter._spec_class
            else:
                return None
        else:
            return type(parameter)

    def get_contained_types(self, parameter):
        contained_types = set()
        if self._is_iterable_container(parameter):
            for contained in parameter:
                contained_types.add(self.get_type(contained))
        return contained_types

    def get_mapped_types(self, parameter):
        mapped_types = set()
        if isinstance(parameter, collections.Mapping):
            for key, value in iteritems(parameter):
                mapped_types.add((self.get_type(key), self.get_type(value)))
        return mapped_types

    @staticmethod
    def _is_iterable_container(parameter):
        return all([
            isinstance(parameter, collections.Container),
            isinstance(parameter, collections.Iterable),
            not isinstance(parameter, basestring),
            not isinstance(parameter, collections.Mapping)
        ])

    @staticmethod
    def _full_name(a_type):
        try:
            return a_type.__module__ + '.' + a_type.__name__
        except AttributeError:
            return

    def __eq__(self, other):
        if not isinstance(other, TypeWrapper):
            return False
        return self.type == other.type and self.contained_types == other.contained_types and self.mapped_types == other.mapped_types

    def __hash__(self):
        return hash(tuple([self.type] + sorted([self._full_name(a_type) for a_type in self.contained_types]) + sorted(
            [(self._full_name(a_type), self._full_name(b_type)) for a_type, b_type in self.mapped_types])))

    def __repr__(self):
        return 'TypeWrapper({}, {}, {})'.format(self.type, self.contained_types, self.mapped_types)

    def __bool__(self):
        return bool(self.type)


class Finding(object):
    def __init__(self):
        self.call_types = defaultdict(set)
        self.return_types = set()
        self.file_name = None
        self.function_name = None
        self.first_line_number = None
        self.docstring = None
        self.variable_names = ()

    def add_call(self, frame, call_types):
        self.__store_constants(frame)
        for key, value in iteritems(call_types):
            self.call_types[key].add(value)
        self.variable_names = tuple([name for name in frame.variable_names if name in call_types])

    def add_return(self, frame, return_type):
        self.__store_constants(frame)
        self.return_types.add(return_type)

    def call_parameters(self):
        for name in self.variable_names:
            if self.call_types[name]:
                yield name, self.call_types[name]

    def __store_constants(self, frame):
        if self.file_name:
            return
        self.file_name = frame.file_name
        self.function_name = frame.function_name
        self.first_line_number = frame.first_line_number
        self.docstring = frame.docstring

    def __gt__(self, other):
        """:type other: Finding"""
        return self.file_name > other.file_name or (self.file_name == other.file_name and
                                                    self.first_line_number > other.first_line_number)

    def __eq__(self, other):
        if not isinstance(other, Finding):
            return False
        return all([
            self.call_types == other.call_types,
            self.return_types == other.return_types,
            self.file_name == other.file_name,
            self.function_name == other.function_name,
            self.first_line_number == other.first_line_number,
            self.docstring == other.docstring,
            self.variable_names == other.variable_names
        ])

    def __repr__(self):
        return ', '.join([
            self.file_name,
            self.function_name,
            str(self.first_line_number),
            str(self.variable_names),
            str(self.call_types),
            str(self.return_types),
        ])


class FrameWrapperFactory(object):
    def __init__(self, included_directories, excluded_parameter_names):
        self.excluded_parameter_names = excluded_parameter_names
        self.included_directories = included_directories

    def create(self, frame, return_value=None):
        return FrameWrapper(frame,
                            self.included_directories,
                            self.excluded_parameter_names,
                            return_value=return_value)


class FrameWrapper(object):
    def __init__(self, frame, included_directories, excluded_parameter_names, return_value=None):
        self.frame = frame
        self.included_directories = included_directories
        self.excluded_parameter_names = excluded_parameter_names
        self.return_value = return_value

    @property
    def file_name(self):
        return get_file_name(self.frame)

    @property
    def function_name(self):
        return get_function_name(self.frame)

    @property
    def first_line_number(self):
        return get_first_line_number(self.frame)

    @property
    def docstring(self):
        return get_docstring(self.frame)

    @property
    def variable_names(self):
        return tuple(
            [name for name in (get_variable_names(self.frame)) if name not in self.excluded_parameter_names])

    @property
    def must_be_stored(self):
        return any(
            (self.file_name.startswith(included_directory) for included_directory in self.included_directories))

    @property
    def call_types(self):
        call_types = {}
        for variable_name in self.variable_names:
            try:
                parameter = get_local_variable(self.frame, variable_name)
            except KeyError:
                continue
            wrapper = TypeWrapper(parameter)
            if wrapper:
                call_types[variable_name] = wrapper
        return call_types

    @property
    def return_type(self):
        if is_generator(self.frame):
            return TypeWrapper(self.return_value, generator=True)
        if self.return_value is None:
            return None
        return TypeWrapper(self.return_value)


def defaultdict_of_finding():
    return defaultdict(Finding)


class Tracer(object):
    def __init__(self, frame_factory, top_level_dir):
        self.top_level_dir = top_level_dir
        self.frame_factory = frame_factory
        self.findings = defaultdict(defaultdict_of_finding)

    def runcall(self, method, *args, **kwargs):
        sys.settrace(self.trace_dispatch)
        method(*args, **kwargs)

    def trace_dispatch(self, frame, event, arg):
        if event == 'call':
            self.on_call(frame)
            return self.trace_dispatch
        if event == 'return':
            self.on_return(frame, arg)

    def on_call(self, frame):
        if get_file_name(frame).startswith(self.top_level_dir):
            wrapped_frame = self.frame_factory.create(frame)
            if wrapped_frame.must_be_stored:
                call_types = wrapped_frame.call_types
                if call_types:
                    self.findings[wrapped_frame.file_name][wrapped_frame.first_line_number].add_call(wrapped_frame,
                                                                                                     call_types)
                    pass

    def on_return(self, frame, return_value):
        if get_file_name(frame).startswith(self.top_level_dir):
            wrapped_frame = self.frame_factory.create(frame, return_value=return_value)
            if wrapped_frame.must_be_stored:
                return_type = wrapped_frame.return_type
                if return_type:
                    self.findings[wrapped_frame.file_name][wrapped_frame.first_line_number].add_return(wrapped_frame,
                                                                                                       return_type)
                    pass

    def all_file_names(self):
        return sorted(self.findings.keys())

    def get_sorted_findings(self, file_name):
        return sorted(self.findings[file_name].values(), reverse=True)


def run(conf):
    factory = FrameWrapperFactory(conf.write_docstrings_in_directories, conf.ignore_call_parameter_names)
    tracer = Tracer(factory, conf.top_level_directory)
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()
    for test_directory in conf.discover_tests_in_directories:
        suite = loader.discover(test_directory, top_level_dir=conf.top_level_directory)
        tracer.runcall(runner.run, suite)
    return tracer
