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
        self._input_layers_config = self.__get_config()

    def __get_config(self) -> list[tuple[str, tuple[int, ...]]]:
        """
        Retrieves the input layers and their dtypes.

        Returns:
            A list of tuples, the first element is related with
                the layer's dtype and the second is its shape.
        """
        input_layers_config = []
        model_config: dict = self.model.get_config()

        # Retrieve the InputLayer's config
        input_layers: list[dict] = [
            l
            for l in model_config.get("layers", [])
            if l.get("class_name") == "InputLayer"
        ]

        # Parse it
        for layer in input_layers:
            config: dict = layer.get("config", {})
            dtype: str = config.get("dtype", "")
            raw_shape: tuple[int, ...] = config.get("batch_input_shape", ())
            shape = raw_shape[1:]
            input_layers_config += [(dtype, shape)]

        return input_layers_config

    def predict(self, sample: numpy.ndarray) -> numpy.ndarray:
        return self.model.predict(sample)

    @property
    def input_shape(self) -> tuple[int, ...]:
        if (num_layers := len(self._input_layers_config)) != 1:
            raise ValueError(
                f"Expected just one input layer, found {num_layers} instead"
            )
        return self._input_layers_config[0][1]

    @property
    def input_dtype(self) -> str:
        if (num_layers := len(self._input_layers_config)) != 1:
            raise ValueError(
                f"Expected just one input layer, found {num_layers} instead"
            )
        return self._input_layers_config[0][0]


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
