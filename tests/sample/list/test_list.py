import unittest

from tests.sample.list.list import get_first_item


class TestList(unittest.TestCase):
    def test_list(self):
        assert get_first_item([1, 2, 3]) == 1