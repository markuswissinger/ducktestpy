import unittest

from original import some, another, yet_another, yet_some


class TestIntegration(unittest.TestCase):
    def test_some(self):
        some()
        another()
        yet_some()
        yet_another()
