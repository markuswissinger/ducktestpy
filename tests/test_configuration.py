import unittest

from hamcrest import assert_that, is_

from ducktest.configuration import DucktestConfiguration


class TestConfiguration(unittest.TestCase):
    def test_creation(self):
        config = DucktestConfiguration(
            __file__,
            'some/path'.split('/'),
            test_directories=['some/path/test'.split('/')],
            write_directories=['some/path/src'.split('/')],
        )
        assert_that(config.top_level_directory, is_('/home/markus/git/ducktestpy/tests/some/path'))
        assert_that(config.discover_tests_in_directories, is_(['/home/markus/git/ducktestpy/tests/some/path/test']))
        assert_that(config.write_docstrings_in_directories, is_(['/home/markus/git/ducktestpy/tests/some/path/src']))
