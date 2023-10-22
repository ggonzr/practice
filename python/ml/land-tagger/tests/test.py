"""
Run all the test suite.
"""
# pylint: disable=unused-import
import unittest
from tests.utils.base import BaseSchemaTest
from tests.file.file import FileTest
from tests.image.image import ImageTest

if __name__ == "__main__":
    unittest.main()
