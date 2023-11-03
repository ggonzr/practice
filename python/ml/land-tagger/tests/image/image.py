"""
This module test that image/image.py module
works properly.
"""
import unittest
import tempfile
from pathlib import Path
from src.file.file import File
from src.image.image import Image


class ImageTest(unittest.TestCase):
    """
    Test the `Image` class.
    """

    def setUp(self) -> None:
        """
        Prepare the test
        """
        self.valid_file = self.__valid_image_file()
        self.raster_file = self.__raster_file()
        self.tmp_file, self.empty_file = self.__create_invalid_file(".jpg")

    def tearDown(self) -> None:
        self.tmp_file.close()

    def __create_invalid_file(self, extension: str):
        """
        Creates an invalid temporal file to test
        behavior in case of errors.
        """
        # pylint: disable=consider-using-with
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w+", encoding="utf-8", suffix=extension
        )
        file: File = File(path=Path(tempfile.gettempdir()).joinpath(tmp_file.name))
        return tmp_file, file

    def __valid_image_file(self) -> File:
        """
        Returns a file object linked
        to a static image.
        """
        image_path: Path = Path("./tests/image/static/cat.jpg").absolute()
        return File(path=image_path)

    def __raster_file(self) -> File:
        """
        Returns a file object linked
        to the example raster file.
        """
        image_path: Path = Path("./tests/image/static/sample.tif").absolute()
        return File(path=image_path)

    def test_load_image(self) -> None:
        """
        Test that it is possible to load an image
        from a valid file.
        """
        image: Image = Image.make(file=self.valid_file)
        expected_resolution = (3456, 5184)
        self.assertEqual(3, image.bands, "Image bands/channels are not the expected.")
        self.assertEqual(
            expected_resolution,
            image.resolution,
            "Image resolution is not the expected.",
        )

    def test_load_invalid_file(self) -> None:
        """
        Test the behavior when an invalid image file
        is loaded.
        """

        def __execute_error(file):
            Image.make(file)

        self.assertRaises(RuntimeError, __execute_error, self.empty_file)

    def test_load_raster(self) -> None:
        """
        Test the behavior when a GeoTIFF image file
        is loaded.
        """
        image: Image = Image.make(file=self.raster_file)
        expected_resolution = (1001, 1001)
        expected_crs: str = "EPSG:32631"

        self.assertIsNotNone(image.metadata, "The raster metadata should be available")
        self.assertNotEqual(
            {},
            image.metadata,
            msg="The raster metadata should be available"
        )
        self.assertEqual(
            image.resolution,
            expected_resolution,
            "The image resolution is not the expected"
        )

        image_crs: str = (
            ""
            if not image.metadata
            else str(image.metadata.get("crs", ""))
        )
        self.assertEqual(
            image_crs,
            expected_crs,
            "The coordinate reference system is not the expected"
        )
