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
import re


class Configuration(object):
    expression = re.compile(r'[^/\\]+')

    def __init__(self, file_path):
        self.options = {
            'write_to': self._add_write_path,
            'do_not_write_to': self._remove_write_path,
            'execute_tests_in': self._add_test_path,
            'do_not_execute_tests_in': self._remove_test_path,
            'exclude_parameter_names': self._exclude_parameter_names,
            'top_level_dir': self._add_top_level_dir,
        }
        self._top_level_directory = ''
        self._test_directories = []
        self._ignore_test_directories = []
        self._write_directories = []
        self._ignore_write_directories = []
        self._ignore_call_parameter_names = []
        self.config_path = os.path.split(file_path)[0]

    @classmethod
    def from_file_path(cls, path):
        configuration = Configuration(path)
        with open(path) as f:
            configuration.read(f)
        return configuration

    @property
    def top_level_directory(self):
        return os.path.join(self.config_path, self._top_level_directory)

    @property
    def discover_tests_in_directories(self):
        return [os.path.join(self.config_path, discover_dir) for discover_dir in self._test_directories]

    @property
    def write_docstrings_in_directories(self):
        return [os.path.join(self.config_path, write_dir) for write_dir in self._write_directories]

    @property
    def ignore_call_parameter_names(self):
        return self._ignore_call_parameter_names

    def __str__(self):
        return 'top_level_directory: {}, discover_tests_in: {}, write_in: {}, ignore_parameter_names: {}'.format(
            self.top_level_directory,
            self.discover_tests_in_directories,
            self.write_docstrings_in_directories,
            self.ignore_call_parameter_names
        )

    def _os_path(self, path):
        return os.path.join(*self.expression.findall(path))

    def _add_write_path(self, paths):
        self._write_directories.extend([self._os_path(path) for path in paths])

    def _remove_write_path(self, paths):
        self._ignore_write_directories.extend([self._os_path(path) for path in paths])

    def _add_test_path(self, paths):
        self._test_directories.extend([self._os_path(path) for path in paths])

    def _remove_test_path(self, paths):
        self._ignore_test_directories.extend([self._os_path(path) for path in paths])

    def _exclude_parameter_names(self, names):
        self._ignore_call_parameter_names.extend(names)

    def _add_top_level_dir(self, paths):
        self._top_level_directory = self._os_path(paths[0])

    def read(self, open_file):
        for line in open_file:
            line = line.split('#')[0]
            words = line.split()
            if words:
                parameter_name = words[0]
                values = words[1:]
                self.options[parameter_name](values)
