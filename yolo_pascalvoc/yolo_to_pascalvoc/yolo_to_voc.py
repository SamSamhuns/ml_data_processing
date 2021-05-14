import os
import cv2
import tqdm
import random
import argparse
import numpy as np
import os.path as osp
from lxml.etree import Element, SubElement, tostring

from utils import cxywh2cxyxy
random.seed(42)


def parse_args():
    parser = argparse.ArgumentParser(
        description='YOLO fmt to Pascal VOC conversion for object detection task')
    parser.add_argument("-r",
                        "--root_yolo",
                        default="yolo",
                        help='root folder containing yolo txt annotation files dir (labels) & images dir (images)')
    parser.add_argument('-l',
                        '--label_file',
                        default='yolo/classes.txt',
                        help='txt file containing class names in newlines')
    parser.add_argument('-e',
                        '--src_img_ext',
                        default='jpg',
                        help='extension of source images. i.e. jpg/JPEG/png/PNG')
    parser.add_argument('-v',
                        '--valid_portion',
                        default=0.1,
                        type=float,
                        help='validation portion. If set to 0, no data saved for validation')
    args = parser.parse_args()
    return args


def load_classes_from_file(txt_file):
    """
    load class name list from txt with contents:
        class1_name
        class2_name
        class3_name
        ...
    """
    class_list = []
    with open(txt_file, 'r') as fclass:
        for class_name in fclass:
            class_list.append(class_name.strip())
    return class_list


def create_VOC2007_dir_struct(root_name="VOCdevkit"):
    """
    creates a PascalYOLO VOC folder struct in the current dir
    root_name
            |--VOC2007
                     |--Annotations
                     |--ImageSets
                                |-- Main
                     |--JPEGImages
    """
    root = osp.join(root_name, "VOC2007")
    os.makedirs(root, exist_ok=True)
    os.makedirs(osp.join(root, "Annotations"), exist_ok=True)
    os.makedirs(osp.join(root, "ImageSets", "Main"), exist_ok=True)
    os.makedirs(osp.join(root, "JPEGImages"), exist_ok=True)


def create_train_val_file_ptr_dict(class_list, root_name="VOCdevkit"):
    """
    Creates the train, val, and trainval files for individual classes
    Returns a dict file pointers file_ptr_dict
    where file_ptr_dict = {CLASS_NAME:((train_path, train_ptr),
                                        (val_path, val_ptr),
                                        (trainval_path, trainval_ptr)),...}
    """
    file_ptr_dict = {}
    for class_name in class_list:
        train_file = osp.join(
            root_name, f"VOC2007/ImageSets/Main/{class_name}_train.txt")
        val_file = osp.join(
            root_name, f"VOC2007/ImageSets/Main/{class_name}_val.txt")
        trainval_file = osp.join(
            root_name, f"VOC2007/ImageSets/Main/{class_name}_trainval.txt")
        file_ptr_dict[class_name] = (open(train_file, 'w'),
                                     open(val_file, 'w'),
                                     open(trainval_file, 'w'))
    return file_ptr_dict


def close_train_val_file_ptr_dict(file_ptr_dict, root_name="VOCdevkit") -> None:
    """
    close file ptrs in the file_ptr_dict
    """
    for fptrs in file_ptr_dict.values():
        [f.close() for f in fptrs]


def generate_voc_xml(img_id, full_imgpath, label_norm, classes, classes_det_flag_dict):
    """
    full_imgpath: path to img file
    """
    img = cv2.imread(full_imgpath)
    img_name = img_id + '.jpg'
    height, width, channels = img.shape

    node_root = Element('annotation')
    node_folder = SubElement(node_root, 'folder')
    node_folder.text = 'VOC2007'
    node_filename = SubElement(node_root, 'filename')
    node_filename.text = img_name
    node_source = SubElement(node_root, 'source')
    node_database = SubElement(node_source, 'database')
    node_database.text = 'YOLO'
    node_size = SubElement(node_root, 'size')
    node_width = SubElement(node_size, 'width')
    node_width.text = str(width)
    node_height = SubElement(node_size, 'height')
    node_height.text = str(height)
    node_depth = SubElement(node_size, 'depth')
    node_depth.text = str(channels)
    node_segmented = SubElement(node_root, 'segmented')
    node_segmented.text = '0'

    # for each detected object
    for j in range(len(label_norm)):
        labels_conv = label_norm[j]
        new_label = cxywh2cxyxy(
            labels_conv[0], width, height, labels_conv[1], labels_conv[2], labels_conv[3], labels_conv[4])
        class_name = classes[new_label[0]]

        node_object = SubElement(node_root, 'object')
        node_name = SubElement(node_object, 'name')
        node_name.text = class_name
        node_pose = SubElement(node_object, 'pose')
        node_pose.text = 'Unspecified'
        node_truncated = SubElement(node_object, 'truncated')
        node_truncated.text = '0'
        node_difficult = SubElement(node_object, 'difficult')
        node_difficult.text = '0'
        node_bndbox = SubElement(node_object, 'bndbox')
        node_xmin = SubElement(node_bndbox, 'xmin')
        node_xmin.text = str(new_label[1])
        node_ymin = SubElement(node_bndbox, 'ymin')
        node_ymin.text = str(new_label[3])
        node_xmax = SubElement(node_bndbox, 'xmax')
        node_xmax.text = str(new_label[2])
        node_ymax = SubElement(node_bndbox, 'ymax')
        node_ymax.text = str(new_label[4])
        xml = tostring(node_root, pretty_print=True)

        # if class exists in current images, set detection flag to 1
        classes_det_flag_dict[class_name] = 1

    return xml


def save_in_voc_fmt(root,
                    classes,
                    source_img_ext="jpg",
                    target_root_name="VOCdevkit",
                    val_portion=0.10,
                    save_loaded_imgs=True):
    """
    converts yolo label fmt into xml label
        root: root path with dirs images, labels and class file
        classes: list of class names ordered by idx
        source_img_ext: extension of source images
        save_loaded_imgs: if images are to re-saved inside VOC2007/JPEGImages
    """
    labelspath = osp.join(root, 'labels')
    labels_list = os.listdir(labelspath)

    if '.DS_Store' in labels_list:
        labels_list.remove('.DS_Store')

    ids_list = [x.split('.')[0] for x in labels_list]
    anno_path_fmt = osp.join(root, 'labels', '%s.txt')
    img_path_fmt = osp.join(root, 'images', f'%s.{source_img_ext}')

    # create voc dir struct
    create_VOC2007_dir_struct(target_root_name)
    # get file ptrs of train, val txt files
    train_val_ptr_dict = create_train_val_file_ptr_dict(classes)
    main_train_ptr = open(
        osp.join(target_root_name, "VOC2007/ImageSets/Main/train.txt"), "w")
    main_val_ptr = open(
        osp.join(target_root_name, "VOC2007/ImageSets/Main/val.txt"), "w")
    main_trainval_ptr = open(
        osp.join(target_root_name, "VOC2007/ImageSets/Main/trainval.txt"), "w")
    # create the template for the out annotation path
    outpath_fmt = osp.join(target_root_name, 'VOC2007',
                           'Annotations', '%s.xml')

    random.shuffle(ids_list)
    train_size = int(len(ids_list) * (1 - val_portion))
    for i in tqdm.tqdm(range(len(ids_list))):
        img_id = ids_list[i]
        full_imgpath = img_path_fmt % img_id
        if not os.path.exists(full_imgpath):     # non-existing img file
            continue
        full_targetpath = (anno_path_fmt % img_id)
        if not os.path.exists(full_targetpath):  # non-existing annotation file
            continue
        label_norm = np.loadtxt(full_targetpath).reshape(-1, 5)
        if len(label_norm) == 0:                 # empty annotation file
            continue

        classes_det_flag_dict = {class_name: -1 for class_name in classes}
        xml = generate_voc_xml(img_id, full_imgpath,
                               label_norm, classes,
                               classes_det_flag_dict)

        # writing to the train, val, trainval txt files for each class
        for class_name, detected in classes_det_flag_dict.items():
            train_fptr, val_fptr, trainval_fptr = train_val_ptr_dict[class_name]
            if i < train_size:  # class training portion
                train_fptr.write(f"{img_id} {detected}\n")
            else:               # class validation portion
                val_fptr.write(f"{img_id} {detected}\n")
            # class train val portion
            trainval_fptr.write(f"{img_id} {detected}\n")

        # writing to the main train, val, trainval txt files
        if i < train_size:  # main training portion
            main_train_ptr.write(f"{img_id}\n")
        else:               # main validation portion
            main_val_ptr.write(f"{img_id}\n")
        # main train val portion
        main_trainval_ptr.write(f"{img_id}\n")

        # write the annotated xml file
        with open(outpath_fmt % img_id, "wb") as fw:
            fw.write(xml)
        # save the loaded file as jpg file
        if save_loaded_imgs:
            cv2.imwrite(osp.join(target_root_name, 'VOC2007', 'JPEGImages',
                                 img_id + '.jpg'), cv2.imread(full_imgpath))

    # close all open pointers for the train,val,trainval files
    close_train_val_file_ptr_dict(train_val_ptr_dict)
    main_train_ptr.close()
    main_val_ptr.close()
    main_trainval_ptr.close()


def main():
    args = parse_args()
    save_in_voc_fmt(root=args.root_yolo,
                    classes=load_classes_from_file(args.label_file),
                    source_img_ext=args.src_img_ext,
                    target_root_name="VOCdevkit",
                    val_portion=args.valid_portion,)


if __name__ == "__main__":
    main()
