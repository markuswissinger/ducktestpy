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

import bdb
import collections
import types
import unittest
from bdb import Bdb
from collections import defaultdict

from future.utils import iteritems
from past.builtins import basestring
from mock import Mock

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
    return frame.f_code.co_consts[0]


class TypeWrapper(object):
    def __init__(self, parameter, generator=False):
        self.is_generator = generator
        self.type = self.get_type(parameter)
        self.contained_types = self.get_contained_types(parameter)

    def get_type(self, parameter):
        if self.is_generator:
            return types.GeneratorType  # self.type
        if isinstance(parameter, Mock) and parameter._spec_class:
            return parameter._spec_class
        else:
            return type(parameter)

    def get_contained_types(self, parameter):
        contained_types = set()
        if self._is_iterable_container(parameter):
            for contained in parameter:
                contained_types.add(TypeWrapper(contained))
        return contained_types

    @staticmethod
    def _is_iterable_container(parameter):
        return all([
            isinstance(parameter, collections.Container),
            isinstance(parameter, collections.Iterable),
            not isinstance(parameter, basestring),
        ])

    def __eq__(self, other):
        if not isinstance(other, TypeWrapper):
            return False
        return self.type == other.type and self.contained_types == other.contained_types

    def __hash__(self):
        return hash((self.type, tuple(sorted(list(self.contained_types)))))

    def __repr__(self):
        return 'TypeWrapper({}, {})'.format(self.type, self.contained_types)


class Finding(object):
    def __init__(self):
        self.call_types = defaultdict(set)
        self.return_types = set()
        self.file_name = None
        self.function_name = None
        self.first_line_number = None
        self.docstring = None

    def add_call(self, frame):
        self.__store_constants(frame)
        for key, value in iteritems(frame.call_types):
            self.call_types[key].add(value)

    def add_return(self, frame):
        self.__store_constants(frame)
        self.return_types.add(frame.return_type)

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
        ])

    def __hash__(self):
        return hash((self.call_types,
                     self.return_types,
                     self.file_name,
                     self.function_name,
                     self.first_line_number,
                     self.docstring))

    def __str__(self):
        return ', '.join([
            self.file_name,
            self.function_name,
            str(self.first_line_number),
            str(self.call_types),
            str(self.return_types),
        ])

    def __repr__(self):
        return str(self)


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

        self.file_name = get_file_name(frame)
        self.function_name = get_function_name(frame)
        self.first_line_number = get_first_line_number(frame)
        self.docstring = get_docstring(frame)

    @property
    def must_be_stored(self):
        for included_directory in self.included_directories:
            if get_file_name(self.frame).startswith(included_directory):
                return True
        return False

    @property
    def call_types(self):
        call_types = {}
        for variable_name in get_variable_names(self.frame):
            if variable_name in self.excluded_parameter_names:
                continue
            try:
                parameter = get_local_variable(self.frame, variable_name)
                wrapper = TypeWrapper(parameter)
                if wrapper.type:
                    call_types[variable_name] = wrapper
            except KeyError:
                pass
        return call_types

    @property
    def return_type(self):
        if is_generator(self.frame):
            return TypeWrapper(self.return_value, generator=True)
        # TODO remove this test in favor of config
        if self.return_value is None:
            return None
        return TypeWrapper(self.return_value)


def defaultdict_of_finding():
    return defaultdict(Finding)


class TypingDebugger(bdb.Bdb):
    def __init__(self, frame_factory):
        Bdb.__init__(self)
        self.frame_factory = frame_factory
        self.findings = defaultdict(defaultdict_of_finding)

    def user_call(self, frame, argument_list):
        wrapped_frame = self.frame_factory.create(frame)
        if wrapped_frame.must_be_stored and wrapped_frame.call_types:
            self.findings[wrapped_frame.file_name][wrapped_frame.first_line_number].add_call(wrapped_frame)

    def user_return(self, frame, return_value):
        wrapped_frame = self.frame_factory.create(frame, return_value=return_value)
        if wrapped_frame.must_be_stored and wrapped_frame.return_type:
            self.findings[wrapped_frame.file_name][wrapped_frame.first_line_number].add_return(wrapped_frame)

    def all_file_names(self):
        return sorted(self.findings.keys())

    def get_sorted_findings(self, file_name):
        return sorted(self.findings[file_name].values(), reverse=True)

    def do_clear(self, arg):
        """there are no breakpoints in current implementation"""
        pass


def run(conf):
    factory = FrameWrapperFactory(conf.write_docstrings_in_directories, conf.ignore_call_parameter_names)
    debugger = TypingDebugger(factory)
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()
    for test_directory in conf.discover_tests_in_directories:
        suite = loader.discover(test_directory, top_level_dir=conf.top_level_directory)
        debugger.runcall(runner.run, suite)
    return debugger
