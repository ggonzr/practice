"""
This module test that file/file.py module works
properly.
"""
import uuid
import tempfile
import unittest
from src.file.file import File


class FileTest(unittest.TestCase):
    """
    Test the `File` class functionalities.
    """

    INVALID_FILE: str = f"{tempfile.gettempdir()}/{uuid.uuid4()}.txt"
    CONTENT: str = "Hello World!"

    def setUp(self) -> None:
        super().setUp()
        # Temporal file
        # pylint: disable=consider-using-with
        self.tmp_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
        self.tmp_file.write(FileTest.CONTENT)
        self.tmp_file.seek(0)

    def tearDown(self) -> None:
        super().tearDown()
        self.tmp_file.close()

    def test_load_file(self) -> None:
        """
        Check that it is possible to load
        a file's content as bytes.
        """
        loaded_file: File = File(path=self.tmp_file.name)
        loaded_file.load()
        parsed_content: str = ""
        if loaded_file.content:
            parsed_content = loaded_file.content.decode("utf-8")
        self.assertEqual(
            parsed_content, FileTest.CONTENT, "The content is not the same as expected"
        )

    def test_invalid_file(self) -> None:
        """
        Check that an exception is raised if
        there are issues loading a file. For instance,
        a file that doesn't exist.
        """

        def __execute_error():
            invalid_file: File = File(path=FileTest.INVALID_FILE)
            invalid_file.load()

        self.assertRaises(FileNotFoundError, __execute_error)
