import unittest

from tests.sample.supertypes.original import some, A, B


class TestIntegration(unittest.TestCase):
    def test_some_a(self):
        some(A())

    def test_some_b(self):
        some(B())
