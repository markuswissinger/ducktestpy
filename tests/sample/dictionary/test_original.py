import unittest

from tests.sample.dictionary.original import some_kwargs


class TestIntegration(unittest.TestCase):
    def test_some_kwargs(self):
        some_kwargs(a=1)