"""
Converts YOLO annotations to COCO JSON annotation format
Directory must be organized in the following structure

        yolo_data_example
            images
                img1.jpg
                img2.jpg
            labels
                img1.txt
                img2.txt
            class.txt/obj.names (list of classnames in newlines)

Sample Usage:
    python yolo_to_coco.py --rd ../yolo_data_example  --cp ../yolo_data_example/classes.txt --is 0 --op coco.json
"""
from pathlib import Path
import argparse
import json
import tqdm

import cv2
import imagesize
import numpy as np

from annotations import (
    create_image_annotation,
    create_annotation_from_yolo_format,
    coco_format_dict,
)


IMG_EXTNS = {".jpg", ".jpeg", ".png"}
IMAGES_DIR = "images"
LABELS_DIR = "labels"


def get_images_info_and_annotations(args):
    """
    Convert yolo annots to coco format
    """
    root_p = args.root_dir
    root_p = Path(root_p)
    if not root_p.is_dir() or not(root_p / IMAGES_DIR).exists() or not(root_p / LABELS_DIR).exists():
        raise ValueError(f"{args.root_dir} must be a dir with subdirs {IMAGES_DIR} and {LABELS_DIR}")

    image_paths = []
    for extn in IMG_EXTNS:
        image_paths += sorted((root_p / IMAGES_DIR).rglob(f"*{extn}"))

    annotations = []
    images_annotations = []
    annotation_id = 1  # In COCO dataset format, annotation_id starts with '1'

    for image_path in tqdm.tqdm(image_paths):
        # image_id follows the format from YOLOv5 val.py json generation
        image_id = int(image_path.stem) if image_path.stem.isnumeric() else image_path.stem

        # Build image annotation, known the image's width and height
        w, h = imagesize.get(str(image_path))
        image_annotation = create_image_annotation(
            file_path=image_path, width=w, height=h, image_id=image_id
        )
        images_annotations.append(image_annotation)

        label_file_name = f"{image_path.stem}.txt"
        label_path = root_p / LABELS_DIR / label_file_name

        if not label_path.exists():
            continue  # The image may not have any applicable annotation txt file.

        with open(str(label_path), "r", encoding="utf-8") as label_file:
            label_read_line = label_file.readlines()

        # yolo format - (class_id, x_center, y_center, width, height)
        # coco format - (annotation_id, x_upper_left, y_upper_left, width, height)
        for label_line in label_read_line:
            # start with category_id with 0 or 1
            category_id = (int(label_line.split()[0]) + args.id_start)
            x_center = float(label_line.split()[1])
            y_center = float(label_line.split()[2])
            width = float(label_line.split()[3])
            height = float(label_line.split()[4])

            float_x_center = w * x_center
            float_y_center = h * y_center
            float_width = w * width
            float_height = h * height

            min_x = int(float_x_center - float_width / 2)
            min_y = int(float_y_center - float_height / 2)
            width = int(float_width)
            height = int(float_height)

            annotation = create_annotation_from_yolo_format(
                min_x,
                min_y,
                width,
                height,
                image_id,
                category_id,
                annotation_id,
                segmentation=args.box2seg,
            )
            annotations.append(annotation)
            annotation_id += 1

    return images_annotations, annotations


def debug_conv(args):
    """
    Debug annotations
    """
    # load class names into list
    with open(args.class_path, "r", encoding="utf-8") as c_ptr:
        class_list = list(map(str.strip, c_ptr.readlines()))

    root_p = args.root_dir
    root_p = Path(root_p)
    if not root_p.is_dir() or not(root_p / IMAGES_DIR).exists() or not(root_p / LABELS_DIR).exists():
        raise ValueError(f"{args.root_dir} must be a dir with subdirs {IMAGES_DIR} and {LABELS_DIR}")

    image_paths = []
    for extn in IMG_EXTNS:
        image_paths += sorted((root_p / IMAGES_DIR).rglob(f"*{extn}"))

    color_list = np.random.randint(low=0, high=256, size=(len(class_list), 3)).tolist()

    for image_path in image_paths:
        print("Image Path : ", image_path)
        # read image file
        img_file = cv2.imread(str(image_path))

        # read .txt label file
        label_file_name = f"{image_path.stem}.txt"
        label_path = root_p / LABELS_DIR / label_file_name
        with open(label_path, "r", encoding="utf-8") as label_ptr:
            label_read_line = label_ptr.readlines()

        for line1 in label_read_line:
            label_line = line1

            category_id = label_line.split()[0]
            x_center = float(label_line.split()[1])
            y_center = float(label_line.split()[2])
            width = float(label_line.split()[3])
            height = float(label_line.split()[4])

            int_x_center = int(img_file.shape[1] * x_center)
            int_y_center = int(img_file.shape[0] * y_center)
            int_width = int(img_file.shape[1] * width)
            int_height = int(img_file.shape[0] * height)

            min_x = int_x_center - int_width / 2
            min_y = int_y_center - int_height / 2
            width = int(img_file.shape[1] * width)
            height = int(img_file.shape[0] * height)

            print("class name :", class_list[int(category_id)])
            print("x_upper_left : ", min_x, "\t", "y_upper_left : ", min_y)
            print("width : ", width, "\t", "\t", "height : ", height)
            print()

            # Draw bounding box
            cv2.rectangle(
                img_file,
                (int(int_x_center - int_width / 2), int(int_y_center - int_height / 2)),
                (int(int_x_center + int_width / 2), int(int_y_center + int_height / 2)),
                color_list[int(category_id)],
                3,
            )

        cv2.imshow(str(image_path), img_file)
        delay = cv2.waitKeyEx()

        # If you press ESC, exit
        if delay == 27 or delay == 113:
            break

        cv2.destroyAllWindows()


def parser_args():
    parser = argparse.ArgumentParser("Yolo format annotations to COCO dataset format")
    parser.add_argument(
        "--rd", "--root_dir", dest="root_dir",
        type=str,
        help="Path to the root data directory with images and labels subdirs",
    )
    parser.add_argument(
        "--cp", "--class_path", dest="class_path",
        type=str,
        help="Path to class.txt or obj.names. File containing class names in newlines",
    )
    parser.add_argument(
        "--is", "--id_start", dest="id_start",
        default=0, type=int, choices=[0, 1],
        help="Whether class id annotation indexes should start with 0 or 1 (default: %(default)s)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Visualize bounding box and print annotation information",
    )
    parser.add_argument(
        "--op", "--output_json_path", dest="output_json_path",
        default="coco_annot.json", type=str,
        help="Path to the converted COCO JSON annotation output (default: %(default)s)",
    )
    parser.add_argument(
        "--box2seg",
        action="store_true",
        help="Coco segmentation will be populated with a polygon "
        "that matches replicates the bounding box data.",
    )
    args = parser.parse_args()
    return args


def main():
    args = parser_args()
    print("Starting YOLO to COCO Conversion")

    # load class names into list
    with open(args.class_path, "r", encoding="utf-8") as c_ptr:
        class_list = list(map(str.strip, c_ptr.readlines()))

    if args.debug is True:
        debug_conv(args)
        print("Debug Finished!")
    else:
        (
            coco_format_dict["images"],
            coco_format_dict["annotations"],
        ) = get_images_info_and_annotations(args)

        # id_start is either set to begin from 0 or 1
        for index, label in enumerate(class_list, start=args.id_start):
            categories = {
                "supercategory": "Defect",
                "id": index,
                "name": label,
            }
            coco_format_dict["categories"].append(categories)

        with open(args.output_json_path, "w", encoding="utf-8") as outfile:
            json.dump(coco_format_dict, outfile, indent=4)

        print("Finished!")


if __name__ == "__main__":
    main()
