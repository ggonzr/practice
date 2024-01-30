"""
This module loads a AI model to use it in
further steps to generate predictions on given
data.
"""
from src.utils.base import Base, dataclass
from src.file.file import File
from src.model.model_interfaces import (
    ModelInterface,
    ModelLoadInterface,
)
from src.model.tensorflow.tensorflow import TensorflowLoader


class Loader:
    """
    Loads the given model using a given file.
    """

    _AVAILABLE_BACKENDS: list[ModelLoadInterface] = [TensorflowLoader()]

    @classmethod
    def load(cls, source: File) -> ModelInterface:
        """
        Loads the model from the given file.
        """
        error: Exception | None = None

        for backend in cls._AVAILABLE_BACKENDS:
            try:
                model: ModelInterface = backend.load(source=source)
                break
            except Exception as e:  # pylint: disable=broad-exception-caught
                error = e

        if error is not None:
            raise RuntimeError(
                f"Unable to load a model from source: {source.path}"
            ) from error

        return model


@dataclass
class Model(Base):
    """
    Represents an AI model to generate predictions.
    """

    source: File
    model: ModelInterface

    def __check_values__(self):
        pass

    @classmethod
    def make(cls, source: File):
        """
        Creates a new file and loads its content.
        """
        model: ModelInterface = Loader.load(source=source)
        return Model(
            source=source,
            model=model,
        )
