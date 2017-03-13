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

import os
import unittest

from ducktest import util
from ducktest.sphinx_docstring import DocstringWriter
from ducktest.typing import CallTypesRepository, ReturnTypesRepository, frame_processors, Tracer
from ducktest.version import VERSION

DUCK_TEST = False, ''


class DucktestConfiguration(object):
    def __init__(
            self, own_path,
            top_level_directory=('',),
            test_directories=None,
            write_directories=None,
            ignore_parameter_names=('self', 'cls'),
            writer_class=DocstringWriter,
            test_loader=None,
            test_runner=None,
    ):
        """
        :param own_path: call this always with __file__
        """
        self._path = os.path.split(own_path)[0]
        self.top_level_directory = self._full_path(top_level_directory)
        self.discover_tests_in_directories = self._directory_list(test_directories)
        self.write_docstrings_in_directories = self._directory_list(write_directories)
        self.ignore_call_parameter_names = ignore_parameter_names
        self.writer_class = writer_class
        self.test_loader = test_loader if test_loader is not None else unittest.TestLoader()
        self.test_runner = test_runner if test_runner is not None else unittest.TextTestRunner(failfast=True)

    def _full_path(self, path_tuple):
        return os.path.join(self._path, *path_tuple)

    def _directory_list(self, path_tuples):
        if path_tuples:
            return [self._full_path(path_tuple) for path_tuple in path_tuples]
        else:
            return [self.top_level_directory]

    def trace_tests(self):
        call_types = CallTypesRepository()
        return_types = ReturnTypesRepository()
        call_frame_processor, return_frame_processor = frame_processors(self, call_types, return_types)
        tracer = Tracer(self.top_level_directory, call_frame_processor, return_frame_processor)

        util.DUCKTEST_TRACE_DISPATCH = tracer.trace_dispatch

        for test_directory in self.discover_tests_in_directories:
            suite = self.test_loader.discover(test_directory, top_level_dir=self.top_level_directory)
            result = tracer.runcall(self.test_runner.run, suite)
            if result.errors or result.failures:
                raise AssertionError('ducktest run aborted on test failure')

        return call_types, return_types

    def run(self):
        print('ducktest {}'.format(VERSION))
        global DUCK_TEST
        DUCK_TEST = True, 'ducktest run'

        call_types, return_types = self.trace_tests()

        self.writer_class(call_types, return_types, self).write_all()
