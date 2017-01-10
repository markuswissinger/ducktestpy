import unittest

from tests.sample.dictionary.original import some_kwargs, another


class TestIntegration(unittest.TestCase):
    def test_some_kwargs(self):
        some_kwargs(a=1)

    def test_another(self):
        another(1, 2)
