import cv2
import numpy as np
from typing import Tuple


def pad_resize_image(cv2_img: np.ndarray,
                     new_size: Tuple[int, int] = (640, 480),
                     color: Tuple[int, int, int] = (125, 125, 125)) -> np.ndarray:
    """
    resize and pad image if necessary, maintaining orig scale
    args:
        cv2_img: numpy.ndarray = cv2 image
        new_size: tuple(int, int) = (width, height)
        color: tuple(int, int, int) = (B, G, R)
    """
    in_h, in_w = cv2_img.shape[:2]
    new_w, new_h = new_size
    # rescale down
    scale = min(new_w / in_w, new_h / in_h)
    # get new sacled widths and heights
    scl_new_w, scl_new_h = int(in_w * scale), int(in_h * scale)
    rsz_img = cv2.resize(cv2_img, (scl_new_w, scl_new_h))
    # calculate deltas for padding
    d_w = max(new_w - scl_new_w, 0)
    d_h = max(new_h - scl_new_h, 0)
    # center image with padding on top/bottom or left/right
    top, bottom = d_h // 2, d_h - (d_h // 2)
    left, right = d_w // 2, d_w - (d_w // 2)
    pad_rsz_img = cv2.copyMakeBorder(rsz_img, top, bottom, left, right,
                                     cv2.BORDER_CONSTANT,
                                     value=color)
    return pad_rsz_img
