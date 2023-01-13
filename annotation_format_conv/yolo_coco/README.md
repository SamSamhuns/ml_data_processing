# Annotation Conversion between YOLO to COCO for Object Detection

Python scripts to convert YOLO into COCO format. It generates JSON annotation files in the COCO format for Object Detection.

Sample yolo data is provided in `../yolo_data_example` and the corresponding PascalVOC example in `VOCdevkit`.

## Pre-requisites

    python 3.7+
    tqdm
    opencv-python
    imagesize

```shell
python3 -m venv venv
pip install -r requirements.txt
```

## YOLO to COCO

### 1. Setup

- Put all your images at `<ROOT_DIR>/images`
- Put corresponding annotations (.txt files) to `<ROOT_DIR>/labels`
- Put the class info file in `VOCdevkit/classes.txt` where each class is in newline in order

YOLO data directory structure: (Sample present in `../yolo_data_example`)

      yolo_data_example/
      ├── images
      │   ├── COCO_train2014_000000000009.jpg
      │   ├── ...
      ├── labels
      │   ├── COCO_train2014_000000000009.txt
      │   ├── ...
      └── classes.txt/obj.names  (list of class names in newlines)

### 2. Conversion

Convert YOLO annotation into a COCO JSON annotation:

```shell
# Note --is flag sets whether class_id should begin with 0 or 1 (YOLOv5 uses 0 indexed class ids)
python yolo_to_coco.py --rd ../yolo_data_example  --cp ../yolo_data_example/classes.txt --is 0 --op coco.json
```

## Visualization

To display the overlaid YOLO/COCO annotations on an image using the `--debug` flag:

```shell
python yolo_to_coco.py --debug --rd ../yolo_data_example  --cp ../yolo_data_example/classes.txt
```
