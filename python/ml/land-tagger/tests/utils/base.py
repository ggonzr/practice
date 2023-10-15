"""
This module test that utils/base.py module
works properly.
"""
import unittest
from dataclasses import dataclass
from src.utils.base import Base


@dataclass
class ExampleSchema(Base):
    """
    Little schema to test the
    capabilities from the `Base`
    data class.
    """

    word: str
    height_cm: int
    height_m: float

    def __check_values__(self):
        if not self.word:
            raise ValueError("Please assign a word!")
        if self.height_m <= 1.8:
            raise ValueError("Please assign a greater height")
        if self.height_m * 100 != self.height_cm:
            raise ValueError("Height is not the same for `m` and `cm` records")


class BaseSchemaTest(unittest.TestCase):
    """
    Test the `Base` data class
    component.
    """

    def test_wrong_types(self):
        """
        Check that an exception is raised
        when values of wrong types are provided
        to the schema.
        """
        error_raised: bool = False
        try:
            _: ExampleSchema = ExampleSchema(
                word=1, height_cm="Hello world!", height_m=1.90
            )
        except TypeError:
            error_raised = True

        self.assertTrue(
            error_raised,
            "A TypeError should be raised due to incorrect types assigned",
        )

    def test_invalid_rules(self):
        """
        Check that a ValueError is raised
        if one of the assigned values
        breaks the schema constraints.
        """
        error_raised: bool = False
        try:
            _: ExampleSchema = ExampleSchema(
                word="Hello world!", height_cm=185, height_m=1.90
            )
        except ValueError:
            error_raised = True

        self.assertTrue(
            error_raised,
            "A TypeError should be raised, the height is not the same",
        )
