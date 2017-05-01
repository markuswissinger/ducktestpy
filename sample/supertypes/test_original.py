import unittest

from sample.supertypes.original import some, A, B, another, yet_another, empty


class TestIntegration(unittest.TestCase):
    def test_some_a(self):
        some(A())

    def test_some_b(self):
        some(B())

    def test_another_a(self):
        another({A(): 1})

    def test_another_B(self):
        another({B(): 2})

    def test_yet_another_a(self):
        yet_another({1: A()})

    def test_yet_another_B(self):
        yet_another({2: B()})

    def test_empty(self):
        empty({})

    def test_empty_a(self):
        empty({A(): 1})
