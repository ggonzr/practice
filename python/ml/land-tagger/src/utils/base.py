"""
This module includes a base data class
implementation to use for other definitions.
Includes method `__validate__()` to check that
fields provided are the same as declared.
"""
from dataclasses import dataclass
import abc


@dataclass
class Base(abc.ABC):
    """
    Little base model to include type checking
    for standard data classes.
    """

    def __new__(cls, *args, **kwargs):
        # pylint: disable=unused-argument
        if cls == Base:
            cause: str = (
                "Cannot instantiate the Base class. "
                "Please use it to build other data classes instead."
            )
            raise TypeError(cause)

        return super().__new__(cls)

    def __validate__(self):
        # pylint: disable=no-member
        model_annotations: dict = self.__annotations__
        type_errors: list[str] = []
        error_num: int = 1

        for name, field_type in model_annotations.items():
            provided_key = self.__dict__[name]
            try:
                type_matches: bool = isinstance(provided_key, field_type)
            except TypeError:
                type_matches = isinstance(provided_key, field_type.__args__)

            if not type_matches:
                type_errors.append(
                    f"{error_num}. The field '{name}' is of type '{type(provided_key)}', but "
                    f"should be of type '{field_type}' instead."
                )
                error_num += 1

        if type_errors:
            cause: str = f"Validation errors for class: {self.__class__}\n"
            cause += "\n".join(type_errors)
            raise TypeError(cause)

    @abc.abstractmethod
    def __check_values__(self):
        """
        Check that all the values comply
        with the desired constraints. If there are multiple
        types allowed, perform a casting if required.

        Raises:
            ValueError: If one field has a value that doesn't
            comply with the desired constraint.
        """

    def __post_init__(self):
        """
        Force that the schema validation
        is executed for the new objects.
        """
        self.__validate__()
        self.__check_values__()
