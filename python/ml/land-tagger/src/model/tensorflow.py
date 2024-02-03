"""
Loads a model from a given file using Tensorflow.
Then, it uses the loaded model to generate predictions.
"""
import numpy
import keras

from src.model.model_interfaces import ModelInterface, ModelLoadInterface
from src.file.file import File


class TensorflowModel(ModelInterface):
    """
    Uses an available Tensorflow model to
    generate predictions.

    Attributes:
        model (keras.Model): Tensorflow model.
    """

    def __init__(self, model: keras.Model) -> None:
        self.model = model

    def predict(self, sample: numpy.ndarray) -> numpy.ndarray:
        return self.model.predict(sample)


class TensorflowLoader(ModelLoadInterface):
    """
    Load a model using Tensorflow as backend.
    """

    def _is_remote_file(self, source: File) -> bool:
        """
        Determines if the given file is available
        in the local filesystem.

        Args:
            source: File to load the model from.

        Returns:
            bool: True if the file is not available
                in the local filesystem nor it is reachable from it.
        """
        return not source.path.exists()

    def load(self, source: File) -> ModelInterface:
        if self._is_remote_file(source=source):
            msg = (
                "Please implement a method to temporarily store "
                "the file into the local filesystem before loading the model. "
            )
            raise NotImplementedError(msg)

        keras_model: keras.Model = keras.models.load_model(filepath=source.path)
        return TensorflowModel(model=keras_model)
