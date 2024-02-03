"""
Run all the test suite.
"""
# pylint: disable=unused-import
import unittest
from tests.utils.base import BaseSchemaTest
from tests.file.file import FileTest
from tests.image.image import ImageTest
from tests.model.model import ModelTest

if __name__ == "__main__":
    unittest.main()
