import unittest

from ducktest.typer import TypeWrapper


class TestTypeWrapper(unittest.TestCase):
    def test_hash(self):
        a = [[1, 2], [3, 4]]
        b = [[1, 2], [3, 4]]

        wrapper_a = TypeWrapper(a)
        wrapper_b = TypeWrapper(b)

        assert wrapper_a == wrapper_b
        assert hash(wrapper_a) == hash(wrapper_b)
