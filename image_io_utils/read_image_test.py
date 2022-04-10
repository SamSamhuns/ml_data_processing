import timeit

import cv2
import pyvips
import imageio
import numpy as np
from PIL import Image


def usingPIL(f):
    im = Image.open(f)
    return np.asarray(im)


def usingImageIO(f):
    arr = imageio.imread(f, pilmode="RGB")
    return np.asarray(arr)


def usingOpenCV(f):
    arr = cv2.imread(f, cv2.IMREAD_UNCHANGED)
    return arr


def usingVIPS(f):
    image = pyvips.Image.new_from_file(f, access="sequential")
    image = image.colourspace("srgb")
    mem_img = image.write_to_memory()
    imgnp = np.frombuffer(mem_img, dtype=np.uint8).reshape(
        image.height, image.width, 3)
    return imgnp


def usingPILandShrink(f):
    im = Image.open(f)
    im.draft('RGB', (1512, 1008))
    return np.asarray(im)


def usingVIPSandShrink(f):
    image = pyvips.Image.new_from_file(f, access="sequential", shrink=4)
    image = image.colourspace("srgb")
    mem_img = image.write_to_memory()
    imgnp = np.frombuffer(mem_img, dtype=np.uint8).reshape(
        image.height, image.width, 3)
    return imgnp


def bench(name):
    result = timeit.timeit(f"using{name}('image.jpg')",
                           setup=f"from __main__ import using{name}",
                           number=10)
    print(f"using{name}: {result * 10} ms")


bench("PIL")
bench("ImageIO")
bench("OpenCV")
bench("VIPS")
bench("PILandShrink")
bench("VIPSandShrink")
