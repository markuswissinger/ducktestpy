import unittest

from tests.sample.raising.original import some


class TestOriginal(unittest.TestCase):
    def test_some(self):
        with self.assertRaises(AttributeError):
            some(None)

    def test_no_raise(self):
        assert 'TrueString' == some('TrueString')
