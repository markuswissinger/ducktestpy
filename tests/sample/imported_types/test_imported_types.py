import unittest

from hamcrest import assert_that, is_

from tests.sample.imported_types.imported_types import use_imported_types
from tests.sample.imported_types.to_import import ToImportA, ToImportB


class TestImportedTypes(unittest.TestCase):
    def test_imported_types(self):
        a = ToImportA()
        b = ToImportB()

        assert_that(use_imported_types(a, b), is_('some result'))
