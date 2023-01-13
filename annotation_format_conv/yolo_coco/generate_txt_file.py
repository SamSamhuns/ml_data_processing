"""
Create a txt file containing all the absolute paths to images files
"""
import os
import glob
import argparse


IMG_EXTNS = {".jpg", ".jpeg", ".png"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a txt file with absolute img paths")
    parser.add_argument(
        "--id", "--image_dir", dest="image_dir", type=str,
        help="Image directory containing all the images.")
    parser.add_argument(
        "--tp", "--txt_path",  dest="txt_path", type=str,
        help="Path to txt file where the absolute image paths will be saved to")
    args = parser.parse_args()
    return args


def agg_img_to_txt(image_dir: str, txt_path: str):
    image_dir = os.path.abspath(image_dir)

    img_paths = glob.glob(os.path.join(image_dir, "*"))
    # filter images by extensions
    img_paths = sorted([p for p in img_paths
                        if os.path.splitext(p)[-1].lower() in IMG_EXTNS])

    with open(txt_path, "w", encoding="utf-8") as txt_f:
        for path in img_paths:
            txt_f.write(path + "\n")
    print(f"----Txt file {txt_path} created----")


def main():
    args = parse_args()
    agg_img_to_txt(args.image_dir, args.txt_path)


if __name__ == "__main__":
    main()
