import os


class DucktestConfiguration(object):
    def __init__(
            self, file_path,
            top_level_directory='',
            test_directories=None,
            write_directories=None,
            ignore_parameter_names=('self','cls'),

    ):
        """
        :param file_path: call this always with __file__
        """
        self.top_level_directory = top_level_directory
        self.test_directories = test_directories if test_directories else top_level_directory
        self.write_directories = write_directories if write_directories else top_level_directory
        self.ignore_parameter_names = ignore_parameter_names
        self.config_path = os.path.split(file_path)[0]
