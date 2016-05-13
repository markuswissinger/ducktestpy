import unittest

from tests.sample.generator import generator


class TestGenerator(unittest.TestCase):
    def test_generator(self):
        for number in generator.some_generator():
            assert number == 1
