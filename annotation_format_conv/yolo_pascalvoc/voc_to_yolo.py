import os
import glob
import shutil
import argparse
import os.path as osp
import xml.etree.ElementTree as ET

from utils import xyxy2cxcywh


def parse_args():
    parser = argparse.ArgumentParser(
        description='Pascal VOC to YOLO fmt conversion')
    parser.add_argument("-r",
                        "--root_voc",
                        default="VOCdevkit/VOC2007",
                        help='Def: VOCdevkit/VOC2007. Root folder containing VOC Annotations, ImageSets, and JPEGImages')
    parser.add_argument('-l',
                        '--class_label_file',
                        default='VOCdevkit/classes.txt',
                        help='Def: VOCdevkit/classes.txt. Txt file containing class names in newlines')
    parser.add_argument('-e',
                        '--src_img_ext_list',
                        nargs='+',
                        default=["jpg", "jpeg"],
                        help='Def: jpg jpeg. List extension of source images. i.e. -e jpg JPEG png PNG')
    parser.add_argument('-c',
                        '--copy_images',
                        action="store_true",
                        help='If -c flag is passed, images are copied from PascalVOC image directory to yolo image directory')
    args = parser.parse_args()
    return args


def get_image_list_from_dir(image_dir, valid_extn=["jpg", "jpeg"]):
    image_list = []
    for ext in valid_extn:
        image_list.extend(glob.glob(osp.join(image_dir, f"*.{ext}")))
    return image_list


def get_class_name_idx_dict(class_label_file):
    """
    get a name ot index dict of classes from a txt file with class names in newlines
    """
    with open(class_label_file, 'r') as class_file:
        class_list = class_file.readlines()
        class_name_idx_dict = {cname.strip(): i for i, cname in enumerate(class_list)}
    return class_name_idx_dict


def convert_voc2yolo_annotation(src_image_path, src_annot_path, class_dict, target_img_dir, target_label_dir):
    basename = osp.basename(src_image_path)
    basename_no_ext = osp.splitext(basename)[0]

    src_annot_file = open(
        src_annot_path, 'r')
    target_annot_file = open(
        osp.join(target_label_dir, basename_no_ext + "txt"), 'w')
    tree = ET.parse(src_annot_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in class_dict or int(difficult) == 1:
            continue
        cls_id = class_dict[cls]
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(
            xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = xyxy2cxcywh((w, h), b)
        target_annot_file.write(str(cls_id) + " " +
                                " ".join([str(a) for a in bb]) + '\n')

    # copy image from PascalVOC to yolo_dir if target_img_dir is not None
    if target_img_dir is not None:
        shutil.copy(src_image_path, osp.join(target_img_dir, basename))


def yolo_to_voc(root_voc_dir, valid_extn, class_label_file, copy_images):
    yolo_dir = 'yolo'
    image_dir = osp.join(root_voc_dir, "JPEGImages")
    annot_dir = osp.join(root_voc_dir, "Annotations")

    yolo_img_dir = osp.join(yolo_dir, "images")
    yolo_label_dir = osp.join(yolo_dir, "labels")
    os.makedirs(yolo_dir, exist_ok=True)
    os.makedirs(yolo_img_dir, exist_ok=True)
    os.makedirs(yolo_label_dir, exist_ok=True)

    if not copy_images:  # if not copy_images, do not copy images from PascalVOC to yolo folder
        yolo_img_dir = None

    class_dict = get_class_name_idx_dict(class_label_file)
    image_paths = get_image_list_from_dir(image_dir, valid_extn=valid_extn)
    for src_image_path in image_paths:
        src_annot_path = osp.join(annot_dir, osp.splitext(
            osp.basename(src_image_path))[0] + ".xml")
        convert_voc2yolo_annotation(src_image_path,
                                    src_annot_path,
                                    class_dict=class_dict,
                                    target_img_dir=yolo_img_dir,
                                    target_label_dir=yolo_label_dir)

    shutil.copy(class_label_file, osp.join(yolo_dir, "classes.txt"))
    print(f"Finished processing images in {image_dir}")


def main():
    args = parse_args()
    yolo_to_voc(root_voc_dir=args.root_voc,
                valid_extn=args.src_img_ext_list,
                class_label_file=args.class_label_file,
                copy_images=args.copy_images)


if __name__ == "__main__":
    main()
