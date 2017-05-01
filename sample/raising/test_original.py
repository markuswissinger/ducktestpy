import unittest

try:
    from ducktest.configuration import DUCK_TEST
except ImportError:
    DUCK_TEST = False, ''
from sample.raising.original import some


class TestOriginal(unittest.TestCase):
    @unittest.skipIf(*DUCK_TEST)
    def test_some(self):
        with self.assertRaises(AttributeError):
            some(None)

    def test_no_raise(self):
        assert 'TrueString' == some('TrueString')
