import unittest

from ducktest.ducktypes import Any


class TestAny(unittest.TestCase):
    def test_subclass(self):
        assert issubclass(int, Any)

    def test_not_subclass(self):
        assert not issubclass(Any, int)

    def test_isinstance(self):
        assert isinstance(3, Any)

    def test_not_isinstance(self):
        assert not isinstance(Any(), int)
