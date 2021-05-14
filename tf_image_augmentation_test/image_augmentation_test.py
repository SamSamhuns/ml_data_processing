import tensorflow as tf
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import argparse
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
tf.compat.v1.enable_eager_execution()  # only for tf 1.x


def combine_imgs_nx3(target_dir, fixed_wh_size=(590, 443)):
    """
    combines images in target_dir in a nx3 grid, where n=num_of_images/3
    all images will be resize to same dimension fixed_wh_size
    """
    images_list = []
    images_name_list = []
    fw, fh = fixed_wh_size
    grid_img_width = 3  # 3 images as img width
    for path, directories, files in os.walk(target_dir):
        for img_name in files:
            img_path = os.path.join(target_dir, img_name)
            images_name_list.append(img_name.split('.')[0])
            images_list.append(Image.open(img_path).resize(fixed_wh_size))

    widths, heights = zip(*(img.size for img in images_list))
    total_width = fw * grid_img_width
    max_height = fh * (len(images_list) // grid_img_width)

    # create new empty img to hold grid
    grid_img = Image.new('RGB', (total_width, max_height))
    aug_draw = ImageDraw.Draw(grid_img)

    x_offset, y_offset = 0, 0
    images_iter = iter(images_list)
    images_name_iter = iter(images_name_list)

    try:
        font = ImageFont.truetype("Arial.ttf", 32)
    except Exception as e:
        print(e, "Usiong default pillow raster font")
        font = ImageFont.load_default()

    for i in range(len(images_list) // grid_img_width):
        x_offset = 0
        for j in range(grid_img_width):
            grid_img.paste(next(images_iter),
                           (x_offset, y_offset))
            aug_draw.text((x_offset, y_offset),
                          next(images_name_iter),
                          font=font,
                          fill=(255, 255, 255, 255))
            x_offset += fw
        y_offset += fh

    grid_img.save("combined_aug_grid.jpg")


def add_random_augs_to_img(img_path, target_dir):
    img_rgb = Image.open(img_path)
    img_rgb = np.array(img_rgb).astype(np.uint8)

    # choose train image preprocessing
    img_rgb = tf.image.central_crop(img_rgb, 0.8)
    img_rgb = tf.image.random_brightness(img_rgb, 1.0)  # needs tuning
    img_rgb = tf.image.random_contrast(img_rgb, 0.1, 0.3)  # needs tuning
    img_rgb = tf.image.random_flip_left_right(img_rgb)
    img_rgb = tf.image.random_flip_up_down(img_rgb)  # need tuning, train err
    img_rgb = tf.image.random_hue(img_rgb, 0.2)
    img_rgb = tf.image.random_jpeg_quality(img_rgb, 75, 95)  # needs tuning
    img_rgb = tf.image.random_saturation(img_rgb, 5.0, 10.0)  # needs tuning

    img = Image.fromarray(img_rgb.numpy(), "RGB")
    img.save(os.path.join(f"{target_dir}/random_aug_img.jpg"))


def add_all_augs_to_img(img_path, target_dir):
    """
    applies 11 augmentations on image from image_path
    and saves them inside target_dir
    """
    orig_img_rgb = Image.open(img_path)
    orig_img_rgb.save(f"{target_dir}/orig_no_aug_img.jpg")

    # gaussian noise requires a float image
    image_rgb = tf.keras.layers.GaussianNoise(
        stddev=0.01)(np.array(orig_img_rgb).astype(np.float32) * 255.0, True) * 255.0
    Image.fromarray(image_rgb.numpy().astype(np.uint8), "RGB").save(
        f"{target_dir}/gaussian_noise_aug_img.jpg")

    # all other augs require uint8, so cast to uint8
    orig_img_rgb = np.array(orig_img_rgb).astype(np.uint8)

    delta = 0.22
    image_rgb = tf.image.adjust_brightness(orig_img_rgb, delta)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/high_brightness_aug_img.jpg")
    image_rgb = tf.image.adjust_brightness(orig_img_rgb, -delta)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/low_brightness_aug_img.jpg")

    image_rgb = tf.image.adjust_contrast(orig_img_rgb, 1.4)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/high_contrast_aug_img.jpg")
    image_rgb = tf.image.adjust_contrast(orig_img_rgb, 0.8)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/low_contrast_aug_img.jpg")

    delta = 0.9
    # WARN: significantly alters image
    image_rgb = tf.image.adjust_hue(orig_img_rgb, delta)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/high_hue_aug_img.jpg")
    # WARN: significantly alters image
    image_rgb = tf.image.adjust_hue(orig_img_rgb, -delta)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/low_hue_aug_img.jpg")

    image_rgb = tf.image.adjust_jpeg_quality(orig_img_rgb, 90)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/high_jpg_quality_aug_img.jpg")
    image_rgb = tf.image.adjust_jpeg_quality(orig_img_rgb, 75)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/low_jpg_quality_aug_img.jpg")

    image_rgb = tf.image.adjust_saturation(orig_img_rgb, 1.5)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/high_saturation_aug_img.jpg")
    image_rgb = tf.image.adjust_saturation(orig_img_rgb, 0.5)
    Image.fromarray(image_rgb.numpy(), "RGB").save(
        f"{target_dir}/low_saturation_aug_img.jpg")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Apply augmentations to image to check results')
    parser.add_argument("-i",
                        "--image_path",
                        default="./test_img.png",
                        help='path of image on which augmentations will be applied')
    parser.add_argument('-t',
                        '--target_dir',
                        default="aug_images",
                        help='path to target dir where augmented images will be saved')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    os.makedirs(args.target_dir, exist_ok=True)
    add_all_augs_to_img(args.image_path, args.target_dir)
    combine_imgs_nx3(args.target_dir)


if __name__ == "__main__":
    main()
