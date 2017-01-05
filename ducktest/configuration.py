import os
import unittest

from ducktest.sphinx_docstring import DocstringWriter
from ducktest.typing import CallTypesRepository, ReturnTypesRepository, frame_processors, Tracer
from ducktest.version import VERSION


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

        no_test_failed = True
        for test_directory in self.discover_tests_in_directories:
            suite = self.test_loader.discover(test_directory, top_level_dir=self.top_level_directory)
            result = tracer.runcall(self.test_runner.run, suite)
            no_test_failed = no_test_failed and not result.errors and not result.failures

        return no_test_failed, call_types, return_types

    def run(self):
        print('ducktest {}'.format(VERSION))

        no_test_failed, call_types, return_types = self.trace_tests()

        if no_test_failed:
            self.writer_class(call_types, return_types, self).write_all()
