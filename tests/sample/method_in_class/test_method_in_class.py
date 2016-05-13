import unittest

from tests.sample.method_in_class import method_in_class


class ModuleMethodTest(unittest.TestCase):
    def test_some_method(self):
        some_class = method_in_class.SomeClass(1)
        assert some_class.some_method(2) == 3
