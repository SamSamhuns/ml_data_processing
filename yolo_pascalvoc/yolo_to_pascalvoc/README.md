# Annotation Convert YOLO to PascalVOC 2007 for Object Detection

A python script to convert YOLO into Pascal VOC 2012 format. It generates xml annotation file in PASCAL VOC format for Object Detection.

## Pre-requisites

    python 3.7+
    tqdm
    opencv-python
    lxml

## Notes

-   Put all your images at `yolo/images`
-   Put corresponding annotations (.txt files) to `yolo/labels`
-   Put the class info file in `yolo/classes.txt`

A sample yolo example is provided in `yolo` and the corresponding PascalVOC example in `VOCdevkit`.

## Usage

To convert a yolo base dataset into Pascal VOC 2007:

```shell
$ python3 yolo_to_voc.py -r YOLO_ROOT -l CLASS_NAME_FILE -e IMG_EXTENSION -v VALIDATION_PORTION
```

By default validation portion is set to 10%, set VALIDATION_PORTION to 0 convert data without validation portion.

To display the overlaid YOLO/PASCAL_VOC annotations on an image:

```shell
$ python3 display_annot.py -ip IMAGE_PATH -at ANNOT_TYPE -ap ANNOT_PATH
```

To overlay yolo annotations to all images in `yolo/images` and save in `yolo_annotated_images`:

```shell
$ python3 add_yolo_annots_to_images.py -i IMAGES_DIR -a ANNOTS_DIR -t TARGET_ANNOTATED_DIR
```
