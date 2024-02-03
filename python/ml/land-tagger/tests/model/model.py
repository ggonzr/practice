"""
This module test the behavior and correctness
for the module `model/model.py`
"""

import unittest
from pathlib import Path
import numpy

from src.file.file import File
from src.model.model import Model
from src.model.tensorflow import TensorflowModel
from src.model.onnx import ONNXModel


class ModelTest(unittest.TestCase):
    """
    Test that it is possible to load a model
    and perform some predictions.
    """

    def setUp(self) -> None:
        super().setUp()

        # Test and expected result values
        # Linear model (2x + 1)
        self.test_values: list[int] = [1, 3, 5]
        self.test_expected_values: list[int] = [3, 7, 11]

        # Tensorflow example: Linear model (2x + 1)
        __tf_example_path = Path(
            "./tests/model/static/linear-two-times-x-plus-one.keras"
        ).absolute()
        self.tf_example_file = File(path=__tf_example_path)

        # PyTorch model (via ONNX): Linear model (2x + 1)
        __onnx_example_path = Path(
            "./tests/model/static/linear-two-times-x-plus-one.onnx"
        ).absolute()
        self.onnx_example_file = File(path=__onnx_example_path)

    def test_load_tensorflow_model(self) -> None:
        """
        Loads a simple linear tensorflow model
        to perform predictions.
        """
        linear_model: Model = Model.make(source=self.tf_example_file)
        self.assertIsNotNone(linear_model, msg="The model object is None")
        self.assertIs(
            linear_model.source,
            self.tf_example_file,
            msg="The source file given is not the same",
        )
        self.assertIsInstance(
            linear_model.model,
            TensorflowModel,
            msg="The implementation class for this case doesn't match",
        )
        self.assertIsNotNone(
            getattr(linear_model.model, "model", None),
            msg="The loaded model should not be a None property",
        )

    def test_prediction_tensorflow_model(self) -> None:
        """
        Perform some simple prediction using the model
        and check the result is the expected.
        """
        linear_model: Model = Model.make(source=self.tf_example_file)
        self.assertEqual(
            len(self.test_values),
            len(self.test_expected_values),
            msg="Please provide the same amount of test values and its expected output",
        )
        result = linear_model.model.predict(sample=numpy.array(self.test_values))
        pred_samples: list[int] = list(result.flatten().astype(int))
        self.assertEqual(
            self.test_expected_values, pred_samples, msg="The prediction doesn't match"
        )

    def test_load_onnx_model(self) -> None:
        """
        Loads a simple linear tensorflow model
        to perform predictions.
        """
        linear_model: Model = Model.make(source=self.onnx_example_file)
        self.assertIsNotNone(linear_model, msg="The model object is None")
        self.assertIs(
            linear_model.source,
            self.onnx_example_file,
            msg="The source file given is not the same",
        )
        self.assertIsInstance(
            linear_model.model,
            ONNXModel,
            msg="The implementation class for this case doesn't match",
        )
        self.assertIsNotNone(
            getattr(linear_model.model, "session", None),
            msg="There should a ONNX inference session here",
        )

    def test_prediction_onnx_model(self) -> None:
        """
        Perform some simple prediction using the model
        and check the result is the expected.
        """
        linear_model: Model = Model.make(source=self.onnx_example_file)
        self.assertEqual(
            len(self.test_values),
            len(self.test_expected_values),
            msg="Please provide the same amount of test values and its expected output",
        )

        # Cast the sample
        prediction = numpy.expand_dims(
            numpy.array(self.test_values, dtype=numpy.float32), axis=1
        )
        result = linear_model.model.predict(prediction)
        pred_samples: list[int] = list(result.flatten().astype(int))
        self.assertEqual(
            self.test_expected_values, pred_samples, msg="The prediction doesn't match"
        )
