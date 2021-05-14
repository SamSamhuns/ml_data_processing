import cv2
import argparse
from utils import cxywh2cxyxy


def parse_args():
    parser = argparse.ArgumentParser(
        description='Object Detection Annotation display for yolo or voc')
    parser.add_argument("-i",
                        "--image_path",
                        default="yolo/images/COCO_train2014_000000000025.jpg",
                        help='path to image where annotations qwill be drawn')
    parser.add_argument('-t',
                        '--type_of_annotation',
                        default='voc',
                        help='Annotation Type: yolo or voc')
    parser.add_argument('-a',
                        '--annot_path',
                        default="VOCdevkit/VOC2007/Annotations/COCO_train2014_000000000025.xml",
                        help='Path to annotation file. Must match with the annotation type')
    args = parser.parse_args()
    return args


def get_xml_annot_for_voc(annot_path):
    from lxml import etree

    final_labels = []
    tree = etree.parse(annot_path)
    root = tree.getroot()
    # iterate through each element in annotation root
    for child in root:
        new_label = [None for _ in range(5)]
        # for each detected obj in image
        if child.tag == "object":
            for subchild in child:
                if subchild.tag == "name":
                    new_label[0] = subchild.text
                elif subchild.tag == "bndbox":
                    for subsubchild in subchild:
                        if subsubchild.tag == "xmin":
                            new_label[1] = int(subsubchild.text)
                        elif subsubchild.tag == "ymin":
                            new_label[2] = int(subsubchild.text)
                        elif subsubchild.tag == "xmax":
                            new_label[3] = int(subsubchild.text)
                        elif subsubchild.tag == "ymax":
                            new_label[4] = int(subsubchild.text)
            final_labels.append(new_label)

    return final_labels


def get_txt_annot_for_yolo(annot_path, width, height):
    import numpy as np

    final_labels = []
    classes_and_annots = np.loadtxt(annot_path).reshape(-1, 5)
    for label in classes_and_annots:
        class_id, xmin, xmax, ymin, ymax = cxywh2cxyxy(
            label[0], width, height, label[1], label[2], label[3], label[4])
        final_labels.append([class_id, xmin, ymin, xmax, ymax])

    return final_labels


def main():
    args = parse_args()
    img = cv2.imread(args.image_path)
    height, width, _ = img.shape

    if args.type_of_annotation == "voc":
        final_labels = get_xml_annot_for_voc(args.annot_path)
    elif args.type_of_annotation == "yolo":
        final_labels = get_txt_annot_for_yolo(args.annot_path, width, height)
    else:
        raise NotImplementedError(
            f"Annotation type {args.type_of_annotation} not supported")

    for classname, xmin, ymin, xmax, ymax in final_labels:
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
        cv2.putText(img,
                    str(classname),
                    (xmin, ymin),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(0, 255, 0),
                    thickness=2)
    cv2.imshow("Image with bboxes", img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
