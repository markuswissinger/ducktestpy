import os

from ducktest.docstring_parser import DocstringWriter

from ducktest import run


def version():
    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(here)
    with open(os.path.join(project_root, 'VERSION.txt')) as f:
        return f.read()


class DucktestConfiguration(object):
    def __init__(
            self, file_path,
            top_level_directory='',
            test_directories=None,
            write_directories=None,
            ignore_parameter_names=('self', 'cls'),

    ):
        """
        :param file_path: call this always with __file__
        """
        self._path = os.path.split(file_path)[0]
        self.top_level_directory = self.in_full(top_level_directory)
        self.discover_tests_in_directories = self.dirlist(test_directories)
        self.write_docstrings_in_directories = self.dirlist(write_directories)
        self.ignore_call_parameter_names = ignore_parameter_names

    def in_full(self, path_particle):
        return os.path.join(self._path, path_particle)

    def dirlist(self, list_of_tuples):
        if list_of_tuples:
            return [self.in_full(os.path.join(contained)) for contained in list_of_tuples]
        else:
            return [self.top_level_directory]

    def run(self):
        """Script entry point"""
        # print('ducktest {}'.format(version()))
        typing_debugger, processors = run(self)

        if typing_debugger:
            DocstringWriter(processors, self.write_docstrings_in_directories).write_all()
