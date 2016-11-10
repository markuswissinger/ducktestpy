import os


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
        self.test_directories = self.dirlist(test_directories)
        self.write_directories = self.dirlist(write_directories)
        self.ignore_parameter_names = ignore_parameter_names

    def in_full(self, path_particle):
        return os.path.join(self._path, path_particle)

    def dirlist(self, list_of_tuples):
        if list_of_tuples:
            return [self.in_full(os.path.join(contained)) for contained in list_of_tuples]
        else:
            return [self.top_level_directory]


config = DucktestConfiguration(__file__, top_level_directory='a', test_directories=['a'])
print config.top_level_directory
print config.test_directories
print config.write_directories
print config.ignore_parameter_names
