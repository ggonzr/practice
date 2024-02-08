"""
This module provides all the interfaces
related with the model schema.
"""

import abc
import numpy
from src.file.file import File
from src.image.image import Image


class ModelInterface(abc.ABC):
    """
    Common operations to use an AI model
    to generate predictions.
    """

    @abc.abstractmethod
    def predict(self, sample: numpy.ndarray) -> numpy.ndarray:
        """
        Generate a prediction using the given sample.

        Args:
            sample: Sample to generate the prediction

        Returns:
            numpy.ndarray: Result prediction.
        """

    @property
    @abc.abstractmethod
    def input_shape(self) -> tuple[int, ...]:
        """
        Returns the dimensions of the input layer

        Returns:
            tuple[int, ...]: A tuple of int describing
                the size of each dimension.
        Raises:
            ValueError: If the model has more than one
                input layer.
        """

    @property
    @abc.abstractmethod
    def input_dtype(self) -> str:
        """
        Returns the expected dtype for the input layer

        Returns:
            str: Input layer dtype.
        Raises:
            ValueError: If the model has more than one
                input layer.
        """


class ModelLoadInterface(abc.ABC):
    """
    Common operations to load a model.
    """

    @abc.abstractmethod
    def load(self, source: File) -> ModelInterface:
        """
        Loads and sets up the model using the given source.

        Args:
            source: Model source path.
        """


class ModelImageInterface(abc.ABC):
    """
    Common interface to transform an image
    to use as a prediction sample for an existing
    model.
    """

    @abc.abstractmethod
    def transform(self, img: Image) -> numpy.ndarray:
        """
        Transforms the given image to use it
        as input for a model.
        """
