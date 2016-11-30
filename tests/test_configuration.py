import unittest

from hamcrest import assert_that, is_

from ducktest.configuration import DucktestConfiguration


class TestConfiguration(unittest.TestCase):
    def test_creation(self):
        config = DucktestConfiguration(
            '/home/user/',
            '/some/path'.split('/'),
            test_directories=['some/path/test'.split('/')],
            write_directories=['some/path/src'.split('/'), 'some/path/write'.split('/')],
        )
        assert_that(config.top_level_directory, is_('/home/user/some/path'))
        assert_that(config.discover_tests_in_directories, is_(['/home/user/some/path/test']))
        assert_that(config.write_docstrings_in_directories, is_([
            '/home/user/some/path/src',
            '/home/user/some/path/write',
        ]))
