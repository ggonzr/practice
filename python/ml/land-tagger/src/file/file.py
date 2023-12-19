"""
Module to handle file loads and basic operations.
"""
import pathlib
import abc
from src.utils.base import Base, dataclass


@dataclass
class File(Base):
    """
    Represents a file that is going to be loaded to parse
    later as an image. This file can be loaded from several
    locations including local filesystems, NFS, cloud filesystems.
    """

    path: pathlib.Path
    content: bytes | None = None

    def __check_values__(self):
        pass

    def load(self) -> bytes:
        """
        Loads the file's content.
        """
        if not self.content:
            Loader.load(file=self)

        content: bytes = b""
        if self.content:
            content = self.content
        return content


class LoaderInterface(abc.ABC):
    """
    Defines some actions to load the file's
    content based on its name extension.
    """

    @abc.abstractmethod
    def load(self, from_path: pathlib.Path) -> bytes:
        """
        Loads the file content as bytes.

        Args:
            from_path: File's location.
        Returns:
            bytes: File's content read as bytes.
        """


class LocalLoader(LoaderInterface):
    """
    Loads the file's content from the
    local filesystem.
    """

    def load(self, from_path: pathlib.Path) -> bytes:
        with open(file=from_path, mode="rb") as f:
            return f.read()


class Loader:
    """
    Based on the file URI scheme and the
    file's extension. Load the content from a given
    file.
    """

    @classmethod
    def __retrieve_loader(cls, file: File) -> LoaderInterface:
        """
        Check the file URI schema and return a loader
        to get the file's content.
        """
        path: pathlib.Path = file.path
        if path.as_uri().startswith("file"):
            return LocalLoader()
        raise NotImplementedError("Unfortunately, there is no loader for your file")

    @classmethod
    def load(cls, file: File) -> File:
        """
        Loads the file's content.
        """
        loader: LoaderInterface = cls.__retrieve_loader(file=file)
        content: bytes = loader.load(file.path)
        file.content = content
        return file
