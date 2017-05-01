import unittest

from sample.dictionary.original import some_kwargs, another, yet_another, some


class TestIntegration(unittest.TestCase):
    def test_some_kwargs(self):
        some_kwargs(a=1)

    def test_another(self):
        another(1)

    def test_yet_another(self):
        yet_another()

    def test_some(self):
        some({})
