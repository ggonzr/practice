"""
This modules models the image and its
content and allows the users to interact with it.
"""
import io
import abc
import numpy
from PIL import Image as PillowImage
from src.utils.base import Base, dataclass
from src.file.file import File


@dataclass
class Image(Base):
    """
    Represents an image, its contents as a numeric
    array and its metadata.
    """

    source: File
    content: numpy.ndarray
    resolution: tuple = (0, 0)
    bands: int = -1
    metadata: dict | None = None

    def __check_values__(self):
        if self.content.size == 0:
            raise ValueError("The image is empty")
        if self.content.ndim < 2:
            raise ValueError("Invalid image dimensions")
        if self.content.ndim == 2:
            # Reshape the array to set the current content
            # as one band
            self.content = numpy.expand_dims(self.content, axis=-1)

        self.bands = self.content.shape[-1]
        self.resolution = self.content.shape[0:2]
        if self.resolution == (0, 0):
            raise ValueError("Invalid image resolution")

    @classmethod
    def make(cls, file: File):
        """
        Creates a new file and loads its content.
        """
        img_array: numpy.ndarray = Loader.load(file=file)
        return Image(source=file, content=img_array)


class ImageInterface(abc.ABC):
    """
    Defines some actions to load an image
    from a file based on its extension.
    """

    @abc.abstractmethod
    def extensions(self) -> set[str]:
        """
        Returns all the image file extensions
        the handler is able to load.

        Returns:
            set[str]: Image file extensions the plugin
                is able to load.
        """

    @abc.abstractmethod
    def load(self, file: File) -> numpy.ndarray:
        """
        Parse the file's content as an image.

        Args:
            from_path: File's location.
        Returns:
            numpy.ndarray: Image file loaded as an
                array.
        """


class PillowLoader(ImageInterface):
    """
    Loads the image from the file's content

    Attributes:
        available_extensions (set[str]): Image files extensions
            to validate if it is possible to load a file with
            this handler.
    """

    def __init__(self) -> None:
        self.available_extensions = self.__compute_extensions()

    def __compute_extensions(self):
        exts = PillowImage.registered_extensions()
        supported_extensions: set[str] = {
            ex for ex, f in exts.items() if f in PillowImage.OPEN
        }
        return supported_extensions

    def extensions(self) -> set[str]:
        return self.available_extensions

    def load(self, file: File) -> numpy.ndarray:
        content: bytes = file.load()
        image = PillowImage.open(io.BytesIO(content))
        img_content = numpy.array(image)
        if img_content.ndim == 2:
            img_content = img_content.transpose((1, 0))
        else:
            img_content = img_content.transpose((1, 0, 2))
        return img_content


class Loader:
    """
    Load the image content as a numeric array.
    """

    HANDLER: list[ImageInterface] = [PillowLoader()]

    @classmethod
    def __retrieve_loader(cls, file: File) -> ImageInterface:
        """
        Check the file extension return a handler
        to load the image.
        """
        extension: str = file.path.suffix
        for plugin in Loader.HANDLER:
            if extension in plugin.extensions():
                return plugin

        error_msg: str = (
            f"Unfortunately, there is no handler for loading a '{extension}' image."
        )
        raise NotImplementedError(error_msg)

    @classmethod
    def load(cls, file: File) -> numpy.ndarray:
        """
        Load the image as a numeric array.
        """
        try:
            handler: ImageInterface = cls.__retrieve_loader(file=file)
            img_array: numpy.ndarray = handler.load(file=file)
            return img_array
        except Exception as e:
            raise RuntimeError("Unable to load the image") from e
