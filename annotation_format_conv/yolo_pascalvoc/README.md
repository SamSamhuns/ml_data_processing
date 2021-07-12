# Annotation Conversion between YOLO and PascalVOC 2007 for Object Detection

Python scripts to convert YOLO into Pascal VOC 2007 format. It generates xml annotation file in PASCAL VOC format for Object Detection.

Sample yolo data is provided in `yolo` and the corresponding PascalVOC example in `VOCdevkit`.

## Pre-requisites

    python 3.7+
    tqdm
    opencv-python
    lxml

## YOLO to PASCAL VOC

### 1. Setup

-   Put all your images at `yolo/images`
-   Put corresponding annotations (.txt files) to `yolo/labels`
-   Put the class info file in `yolo/classes.txt` where each class is in newline in order

YOLO data directory structure:

      yolo/
      ├── classes.txt
      ├── images
      │   ├── COCO_train2014_000000000009.jpg
      │   └── ...
      └── labels
          ├── COCO_train2014_000000000009.txt
          └── ...

### 2. Conversion

To convert a yolo base dataset into Pascal VOC 2007:

```shell
$ python3 yolo_to_voc.py -r ROOT_YOLO -l CLASS_NAME_FILE -e IMG_EXTENSION -v VALIDATION_PORTION
```

By default validation portion is set to 10%, set VALIDATION_PORTION to 0 convert data without validation portion.

To overlay yolo annotations to all images in `yolo/images` and save in `yolo_annotated_images`:

```shell
$ python3 add_yolo_annots_to_images.py -i IMAGES_DIR -a ANNOTS_DIR -t TARGET_ANNOTATED_DIR
```

## PASCAL VOC to YOLO

### 1. Setup

-   Put all your images at `VOCdevkit/VOC/JPEGImages`
-   Put corresponding annotations (.xml files) to `VOCdevkit/VOC/Annotations`
-   Put the class info file in `VOCdevkit/classes.txt` where each class is in newline in order

PascalVOC 2007 data directory structure:

      VOCdevkit/
      ├── VOC2007
      │   ├── Annotations
      │   │   ├── COCO_train2014_000000000009.xml
      │   │   ├── ...
      │   ├── ImageSets
      │   │   └── Main
      │   │       ├── airplane_train.txt
      │   │       ├── airplane_trainval.txt
      │   │       ├── airplane_val.txt
      │   │       ├── ...
      │   └── JPEGImages
      │       ├── COCO_train2014_000000000009.jpg
      │       ├── ...
      └── classes.txt

### 2. Conversion

o convert a Pascal VOC 2007 dataset into a yolo dataset:

```shell
$ python3 voc_to_yolo.py -r ROOT_VOC -l CLASS_NAME_FILE -e IMG_EXTENSION -c
```

Note: Including the `-c` flag copies the image from PascalVOC to the new YOLO directory

## Visualization

To display the overlaid YOLO/PASCAL_VOC annotations on an image:

```shell
$ python3 display_annot.py -ip IMAGE_PATH -at ANNOT_TYPE -ap ANNOT_PATH
```
