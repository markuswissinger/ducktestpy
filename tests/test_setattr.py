import unittest

from ducktest.setattr_write import Context


class TestSourceContext(unittest.TestCase):
    def test_repr(self):
        file_context=Context('SomeFile')
        class_context=Context('SomeClass(object):\n')
        class_context._contained=['pass\n']
        file_context._contained=['blaBlaBla\n', class_context]
        print(file_context)