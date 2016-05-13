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

import unittest

from hamcrest import assert_that, is_

from ducktest import Configuration


class ConfigReaderTest(unittest.TestCase):
    def test_expression(self):
        regex = Configuration.expression
        result = regex.findall('/home/test/project')
        assert_that(result, is_(['home', 'test', 'project']))

    def test_expression_win(self):
        regex = Configuration.expression
        result = regex.findall(r'\home\test\project')
        assert_that(result, is_(['home', 'test', 'project']))

    def test_reading(self):
        config_file = iter([
            'top_level_dir           py/\n',
            'execute_tests_in        py/demo/\n',
            'write_to                py/demo/\n',
            'exclude_parameter_names self\n',
            'exclude_parameter_names cls\n',
        ])
        configuration = Configuration('/home/test/project/')
        configuration.read(config_file)

        assert_that(configuration.top_level_directory, is_('/home/test/project/py'))
        assert_that(configuration.ignore_call_parameter_names, is_(['self', 'cls']))
        assert_that(configuration.discover_tests_in_directories, is_(['/home/test/project/py/demo']))
        assert_that(configuration.write_docstrings_in_directories, is_(['/home/test/project/py/demo']))

    def test_comments(self):
        config_file = iter([
            ' # top_level_dir           py/\n',
        ])
        configuration = Configuration('/home/test/project/')
        configuration.read(config_file)

        assert_that(configuration.top_level_directory, is_('/home/test/project/'))

    def test_empty_file(self):
        config_file = iter([''])
        configuration = Configuration('/home/test/project/')
        configuration.read(config_file)

        assert_that(configuration.top_level_directory, is_('/home/test/project/'))
        assert_that(configuration.write_docstrings_in_directories, is_(['/home/test/project']))
        assert_that(configuration.discover_tests_in_directories, is_(['/home/test/project']))
        assert_that(configuration.ignore_call_parameter_names, is_([]))
