import unittest

from tests.sample.module_constants.original import some, another


class TestIntegration(unittest.TestCase):
    def test_some(self):
        assert list(some()) == ['A', 'B']

    def test_another(self):
        assert list(another(['C'])) == ['A', 'B', 'C']
