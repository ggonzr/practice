"""
Loads a model from a ONNX file
to perform predictions.
"""

import re
import types
import numpy

# pylint: disable=import-error, no-name-in-module
from onnx.mapping import TENSOR_TYPE_MAP
import onnxruntime as ort
from src.model.model_interfaces import ModelInterface, ModelLoadInterface
from src.file.file import File


def _onnx_get_match_to_numpy() -> dict[str, str]:
    """
    Retrieves a dictionary to match the ONNX tensor type
    with its numpy dtype analogous.

    Returns:
        dict[str, str]: Matching relationship
    """
    as_np_types = {
        dt.name.split(".")[1].lower(): str(dt.np_dtype)
        for dt in TENSOR_TYPE_MAP.values()
    }
    return as_np_types


# Inmutable match
_onnx_to_numpy = types.MappingProxyType(_onnx_get_match_to_numpy())

# Extract the dtype
_onnx_get_dtype = re.compile(r"^tensor\(([a-z0-9]+)\)")


class ONNXModel(ModelInterface):
    """
    Uses an available ONNX model to
    generate predictions.

    Attributes:
        session (ort.InferenceSession): ONNX session to run predictions.
    """

    def __init__(self, session: ort.InferenceSession) -> None:
        self.session = session

    def predict(self, sample: numpy.ndarray) -> numpy.ndarray:
        outputs = self.session.run(None, {"input": sample})
        return outputs[0]

    @property
    def input_shape(self) -> tuple[int, ...]:
        model_inputs = self.session.get_inputs()
        if (num_layers := len(model_inputs)) != 1:
            raise ValueError(
                f"Expected just one input layer, found {num_layers} instead"
            )
        return tuple(model_inputs[0].shape)

    @property
    def input_dtype(self) -> str:
        model_inputs = self.session.get_inputs()
        if (num_layers := len(model_inputs)) != 1:
            raise ValueError(
                f"Expected just one input layer, found {num_layers} instead"
            )

        dtype: str = model_inputs[0].type
        potential_dtypes: list[str] = _onnx_get_dtype.findall(dtype)
        if not potential_dtypes:
            raise ValueError("Unable to extract the dtype from the ONNX layer")

        found_dtype = potential_dtypes[0]
        matched_dtype: str = _onnx_to_numpy[found_dtype]
        return matched_dtype


class ONNXLoader(ModelLoadInterface):
    """
    Load a model using ONNX.
    """

    def load(self, source: File) -> ModelInterface:
        onnx_inference: ort.InferenceSession = ort.InferenceSession(source.load())
        return ONNXModel(session=onnx_inference)
