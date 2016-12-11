import os

from ducktest.sphinx_docstring import DocstringWriter
from ducktest.typing import run
from ducktest.version import VERSION


class DucktestConfiguration(object):
    def __init__(
            self, own_path,
            top_level_directory=('',),
            test_directories=None,
            write_directories=None,
            ignore_parameter_names=('self', 'cls'),

    ):
        """
        :param own_path: call this always with __file__
        """
        self._path = os.path.split(own_path)[0]
        self.top_level_directory = self._in_full(top_level_directory)
        self.discover_tests_in_directories = self._dirlist(test_directories)
        self.write_docstrings_in_directories = self._dirlist(write_directories)
        self.ignore_call_parameter_names = ignore_parameter_names

    def _in_full(self, path_tuple):
        return os.path.join(self._path, *path_tuple)

    def _dirlist(self, path_tuples):
        if path_tuples:
            return [self._in_full(path_tuple) for path_tuple in path_tuples]
        else:
            return [self.top_level_directory]

    def run(self):
        print('ducktest {}'.format(VERSION))

        no_test_failed, call_types, return_types = run(self)

        if no_test_failed:
            DocstringWriter(call_types, return_types, self.write_docstrings_in_directories).write_all()
