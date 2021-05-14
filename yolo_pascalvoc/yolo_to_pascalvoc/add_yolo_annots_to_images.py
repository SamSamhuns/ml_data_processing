import os
import cv2
import glob
import tqdm
import argparse
import os.path as osp


def parse_args():
    parser = argparse.ArgumentParser(
        description='Add yolo annotations to images')
    parser.add_argument("-i",
                        "--images",
                        default="yolo/images",
                        help='folder containing iamges for annotation')
    parser.add_argument('-a',
                        '--annots',
                        default='yolo/labels',
                        help='folder containing yolo annotation txt files')
    parser.add_argument('-t',
                        '--target_dir',
                        default='yolo_annotated_images',
                        help='target dir where annotated images are saved')
    args = parser.parse_args()
    return args


def xywh2xyxy(x, y, w, h, dw, dh):
    x1 = int((x - w / 2) * dw)
    x2 = int((x + w / 2) * dw)
    y1 = int((y - h / 2) * dh)
    y2 = int((y + h / 2) * dh)

    if x1 < 0:
        x1 = 0
    if y1 > dw - 1:
        y1 = dw - 1
    if y1 < 0:
        y1 = 0
    if y2 > dh - 1:
        y2 = dh - 1
    return x1, y1, x2, y2


def add_annots_to_imgs(img_root_dir, annot_root_dir, target_drawn_dir):
    os.makedirs(target_drawn_dir, exist_ok=True)
    img_list = sorted(glob.glob(f"{img_root_dir}/*.jpg"))
    label_dict = {"0": ["blue", (255, 0, 0)],
                  "1": ["red", (0, 0, 255)],
                  "2": ["idle", (0, 255, 0)],
                  "3": ["punch", (0, 255, 0)],
                  "4": ["kick", (0, 255, 0)],
                  "5": ["clinch", (0, 255, 0)],
                  "6": ["ground", (0, 255, 0)],
                  "7": ["punch_unclear", (0, 255, 0)],
                  "8": ["kick_unclear", (0, 255, 0)]}

    for img_file in tqdm.tqdm(img_list):
        frame_num = osp.basename(img_file).split('.')[0]
        annot_file = f"{annot_root_dir}/" + frame_num + ".txt"
        with open(annot_file, 'r') as annot_ptr:
            img_cv = cv2.imread(img_file)
            img_cv = cv2.resize(img_cv, (576 * 2, 360 * 2))
            height, width, _ = img_cv.shape
            for line in annot_ptr:
                line = line.strip().split()
                label = line[0]
                cx, cy, rw, rh = float(line[1]), float(
                    line[2]), float(line[3]), float(line[4])

                x1, y1, x2, y2 = xywh2xyxy(cx, cy, rw, rh, width, height)
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.putText(img_cv,
                            label_dict[label][0],
                            (x1, y1),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=2,
                            thickness=2,
                            color=label_dict[label][1])
                cv2.rectangle(img_cv,
                              (x1, y1),
                              (x2, y2),
                              color=label_dict[label][1],
                              thickness=2)
            cv2.imwrite(f"{target_drawn_dir}/{frame_num}.jpg", img_cv)


def main():
    args = parse_args()
    add_annots_to_imgs(args.images, args.annots, args.target_dir)


if __name__ == "__main__":
    main()
