# Machine Learning Data Processing Tools

Tools for data filtering, preprocessing, and format conversion for ML tasks.

Currently support is only present for Computer Vision tasks

### Data Processing

-   [Tensorflow Image Augmentation Test](tf_image_augmentation_test)

<center>
<img src="tf_image_augmentation_test/combined_aug_grid.jpg" width="50%" />
</center>

-   [Training Data Filtering for Image Classification & Segmentation](training_data_cls_seg_filter)

|                                          <center>Good Matting</center>                                          |                                          <center>Bad Matting</center>                                          |
| :-------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------: |
| <img src="training_data_cls_seg_filter/seg_training_data_filtering/screenshots/good_matting.jpg" width="60%" /> | <img src="training_data_cls_seg_filter/seg_training_data_filtering/screenshots/bad_matting.jpg" width="60%" /> |

-   [YOLO and Pascal VOC conversion for Object Detection Training](annotation_format_conv)

PASCAL VOC2007

        <annotation>
          <folder>VOC2007</folder>
          <filename>COCO_train2014_000000000025.jpg</filename>
          <source>
            <database>YOLO</database>
          </source>
          <size>
            <width>640</width>
            <height>426</height>
            <depth>3</depth>
          </size>
          <segmented>0</segmented>
          <object>
            <name>zebra</name>
            <pose>Unspecified</pose>
            <truncated>0</truncated>
            <difficult>0</difficult>
            <bndbox>
              <xmin>385</xmin>
              <ymin>60</ymin>
              <xmax>600</xmax>
              <ymax>357</ymax>
            </bndbox>
          </object>
        </annotation>

YOLO format

    23 0.770336 0.489695 0.335891 0.697559


### Data Acquisition

-   [Youtube Downloader](youtube_downloader)
