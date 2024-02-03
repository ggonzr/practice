"""
Loads a model from a ONNX file
to perform predictions.
"""

import numpy
import onnxruntime as ort
from src.model.model_interfaces import ModelInterface, ModelLoadInterface
from src.file.file import File


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


class ONNXLoader(ModelLoadInterface):
    """
    Load a model using ONNX.
    """

    def load(self, source: File) -> ModelInterface:
        onnx_inference: ort.InferenceSession = ort.InferenceSession(source.load())
        return ONNXModel(session=onnx_inference)
