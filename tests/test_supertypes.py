import unittest

from ducktest.supertypes import is_true_subclass_of


class A(object):
    pass


class B(A):
    pass


class TestSuperTypes(unittest.TestCase):
    def test_some(self):
        assert is_true_subclass_of(B, A)

    def test_some1(self):
        assert not is_true_subclass_of(A, A)

    def test_some2(self):
        assert not is_true_subclass_of(A, B)

    def test_some3(self):
        assert not is_true_subclass_of(B, B)
