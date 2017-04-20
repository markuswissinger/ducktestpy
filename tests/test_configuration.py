import os
import unittest
from hamcrest import assert_that, is_

from ducktest.configuration import DucktestConfiguration


class TestConfiguration(unittest.TestCase):
    def test_creation(self):
        config = DucktestConfiguration(
            __file__,
            '/some/path'.split('/'),
            test_directories=['some/path/test'.split('/')],
            write_directories=['some/path/src'.split('/'), 'some/path/write'.split('/')],
        )

        path = os.path.split(__file__)[0]

        assert_that(config.top_level_directory, is_(os.path.join(path, 'some', 'path')))
        assert_that(config.discover_tests_in_directories, is_([os.path.join(path, 'some', 'path', 'test')]))
        assert_that(config.write_docstrings_in_directories, is_([
            os.path.join(path, 'some', 'path', 'src'),
            os.path.join(path, 'some', 'path', 'write'),
        ]))
