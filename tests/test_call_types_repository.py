import unittest
from collections import namedtuple

from ducktest.another_typer import CallTypesRepository

Code = namedtuple('Code', ['co_filename', 'co_firstlineno'])


class Frame(object):
    def __init__(self, file_name, line_number):
        self.f_code = Code(file_name, line_number)


class TestCallTypesRepository(unittest.TestCase):
    def test_store(self):
        frame = Frame('some_file', 67)

        call_types=CallTypesRepository()
        call_types.store('a_name', type(1), frame)
