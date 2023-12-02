from __future__ import annotations
# from .data import ERROR_ICON_PNG
from PIL import Image, ImageTk
from pathlib import Path
import functools, io

# IMAGE_DATA = {
#     'error': ERROR_ICON_PNG
# }

# ROOTDIR = Path(__file__).parent

IMAGE_FILES = {
    'error': "error.png",
    'info': "info.png"
}

@functools.cache
def load_image(name: str, /):
    """
    Load an image with the given NAME.

    NAME can be one of the following:
    - error
    """
    try:
        image_file = Path(__file__).parent / IMAGE_FILES[name]
        data = image_file.read_bytes()
        # data = IMAGE_DATA[name]
    except:
        raise ValueError(f"Unknown image {name!r}")

    with io.BytesIO(data) as fd:
        img = Image.open(fd)
        img.load()

    return ImageTk.PhotoImage(img)
