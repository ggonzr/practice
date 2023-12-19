"""
This modules models the image and its
content and allows the users to interact with it.
"""
import io
import abc
import numpy
import rasterio
import rasterio.drivers
import rasterio.plot
import PIL.Image
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
        if self.content.ndim < 3:
            raise ValueError("Invalid image dimensions")

        self.bands = self.content.shape[-1]
        self.resolution = self.content.shape[0:2]
        if self.resolution == (0, 0):
            raise ValueError("Invalid image resolution")

    @classmethod
    def make(cls, file: File):
        """
        Creates a new file and loads its content.
        """
        img_array, metadata = Loader.load(file=file)
        return Image(
            source=file,
            content=img_array,
            metadata=metadata
        )


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
                is able to load. All the extensions
                should start with a dot, e.g: .jpg
        """

    @abc.abstractmethod
    def load(self, file: File) -> tuple[numpy.ndarray, dict]:
        """
        Parse the file's content as an image.

        Args:
            from_path: File's location.
        Returns:
            numpy.ndarray: Image file loaded as an
                array.
            dict: Image metadata
        """

    @abc.abstractmethod
    def arrange_dims(self, content: numpy.ndarray) -> numpy.ndarray:
        """
        Reorders the image dimensions to match the
        following schema: (height, width, channels)

        Args:
            content (numpy.ndarray): Image content
        Returns
            numpy.ndarray: Image content with the axis rearranged.
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

    def __compute_extensions(self) -> set[str]:
        exts = PIL.Image.registered_extensions()
        supported_extensions: set[str] = {
            ex for ex, f in exts.items() if f in PIL.Image.OPEN
        }
        return supported_extensions

    def __get_metadata(self, image: PIL.Image.Image) -> dict:
        """
        Retrieves some metadata from the image.
        """
        return {
            "size": image.size,
            "height": image.height,
            "width": image.width,
            "format": image.format,
            "mode": image.mode,
        }

    def extensions(self) -> set[str]:
        return self.available_extensions

    def arrange_dims(self, content: numpy.ndarray) -> numpy.ndarray:
        # Image from PIL package already uses this convention.
        return content

    def load(self, file: File) -> tuple[numpy.ndarray, dict]:
        content: bytes = file.load()
        image = PIL.Image.open(io.BytesIO(content))
        img_content = numpy.array(image, dtype=numpy.int32)
        img_metadata = self.__get_metadata(image=image)
        return img_content, img_metadata


class RasterIOLoader(ImageInterface):
    """
    Loads a geospatial image from the file's content.

    Attributes:
        available_extensions (set[str]): Image files extensions
            to validate if it is possible to load a file with
            this handler.
    """

    def __init__(self) -> None:
        self.available_extensions = self.__compute_extensions()

    def __compute_extensions(self) -> set[str]:
        # Only use this loader for GeoTIFF images.
        desired_exts: set[str] = {"tif", "tiff"}
        all_exts: set[str] = (
            set(
                rasterio
                .drivers
                .raster_driver_extensions()
            )
        )
        exts: set[str] = desired_exts & all_exts
        return {f".{ext}" for ext in exts}

    def __get_metadata(self, raster) -> dict:
        """
        Retrieves some metadata from the raster.
        """
        return raster.meta

    def extensions(self) -> set[str]:
        return self.available_extensions

    def arrange_dims(self, content: numpy.ndarray) -> numpy.ndarray:
        return rasterio.plot.reshape_as_image(content)

    def load(self, file: File) -> tuple[numpy.ndarray, dict]:
        content: io.BytesIO = io.BytesIO(file.load())
        with rasterio.open(
            fp=content,
            mode="r",
            driver="GTiff",
            dtype=numpy.int32
        ) as rf:
            img_content: numpy.ndarray = rf.read()
            img_content = self.arrange_dims(content=img_content)
            metadata: dict = self.__get_metadata(raster=rf)
            return img_content, metadata


class Loader:
    """
    Load the image content as a numeric array.
    """

    HANDLER: list[ImageInterface] = [
        RasterIOLoader(),
        PillowLoader()
    ]

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
    def load(cls, file: File) -> tuple[numpy.ndarray, dict]:
        """
        Load the image as a numeric array.
        """
        try:
            handler: ImageInterface = cls.__retrieve_loader(file=file)
            return handler.load(file=file)
        except Exception as e:
            raise RuntimeError("Unable to load the image") from e
