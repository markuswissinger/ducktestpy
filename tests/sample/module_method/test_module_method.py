import unittest

from tests.sample.module_method import module_method


class ModuleMethodTest(unittest.TestCase):
    def test_some_method(self):
        assert module_method.some_method(1) == 1
