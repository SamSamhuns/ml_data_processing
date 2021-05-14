def cxywh2cxyxy(class_id, width, height, x, y, w, h):
    """
    converts the normalized positions into integer position
    coord conv from xywh to xyxy + class id return
    """
    xmax = int((x * width) + (w * width) / 2.0)
    xmin = int((x * width) - (w * width) / 2.0)
    ymax = int((y * height) + (h * height) / 2.0)
    ymin = int((y * height) - (h * height) / 2.0)
    class_id = int(class_id)
    return (class_id, xmin, xmax, ymin, ymax)
