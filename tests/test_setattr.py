import unittest

from ducktest.setattr_write import Tokens


class TestGenerate(unittest.TestCase):
    def test_some(self):
        start_token = Tokens(None, [])
        start_token.add_child('BLA')
        second = Tokens(start_token, ['blubb'])
        start_token.add_child(second)
        for definition in start_token.definitions():
            print(definition)

        print(start_token.definition)
        print(second.definition)
