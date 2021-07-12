def cxcywh2xyxy(class_id, width, height, x, y, w, h):
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


def xyxy2cxcywh(size, box):
    """
    convert x0,x1,y0,y1 to norm cx,cy,w,h
    size = (width, height), box = []
    """
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)
