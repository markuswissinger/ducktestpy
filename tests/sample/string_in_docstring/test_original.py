import unittest

from tests.sample.string_in_docstring.original import some


class TestIntegration(unittest.TestCase):
    def test_some(self):
        some()
