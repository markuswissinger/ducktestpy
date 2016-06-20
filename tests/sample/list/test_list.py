import unittest

from tests.sample.list.list import get_first_item


class TestList(unittest.TestCase):
    def test_list(self):
        assert get_first_item([1, 2, 3]) == 1

    def test_list_again(self):
        assert get_first_item([1, 2, 3, 4]) == 1

    def test_list_of_strings(self):
        assert get_first_item(['1', '2', '3', '4']) == '1'

    def test_mixed(self):
        assert get_first_item([[1, 2, 3], '2', 3]) == [1, 2, 3]
