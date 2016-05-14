import unittest

from tests.sample.classmethod.classmethod import AnotherClass


class ClassMethodTest(unittest.TestCase):
    def test_classmethod(self):
        assert AnotherClass.some_classmethod(1) == 2
