import unittest

from tests.sample.module_constants.original import some


class TestIntegration(unittest.TestCase):
    def test_some(self):
        assert list(some()) == ['A', 'B']
