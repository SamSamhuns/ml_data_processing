import pandas as pd
import argparse
import cv2
import os


def load_existing_records(f):
    seen = {}
    if os.path.exists(f):
        try:
            seen = pd.read_csv(f, header=None, index_col=0).T.to_dict('list')
        except Exception as e:
            print(e)
            return
        good_cases = len([v[1] for v in seen.values() if v[1] == 1])
        print(f'Found {good_cases} good cases out of {len(seen)} total records')
    else:
        print('found 0 records')
    return seen


def gather_imgs(root_dir):
    for root, _, files in os.walk(root_dir):
        for f in sorted(files):
            yield os.path.join(root, f)


def save_images(f, img_root, matting_root):
    seen_from_file = load_existing_records(f)
    print(seen_from_file)

    img_collection = gather_imgs(img_root)
    matting_collection = gather_imgs(matting_root)

    os.makedirs(img_root + '_OUT', exist_ok=True)
    os.makedirs(matting_root + '_OUT', exist_ok=True)

    i = 0
    for img_path, matting_path in zip(img_collection, matting_collection):
        img_path_base = os.path.basename(img_path)
        matting_path_base = os.path.basename(matting_path)

        img_ok = True if seen_from_file[img_path][1] == 1 else False
        if img_ok:
            i += 1
            img = cv2.imread(img_path)
            try:
                mask = cv2.imread(matting_path, cv2.IMREAD_UNCHANGED)[:, :, 3]
            except Exception as e:
                mask = cv2.imread(matting_path, cv2.IMREAD_UNCHANGED)
            cv2.imwrite(img_root + f'_OUT/{img_path_base}', img)
            cv2.imwrite(matting_root + f'_OUT/{matting_path_base}', mask)
    print(i, f'images saved in {img_root}_OUT')


def main():
    parser = argparse.ArgumentParser(description='Image filtering')
    parser.add_argument('-c', '--clip_root', type=str,
                        help='root path of orig/clip images', default="sample_data/img_orig")
    parser.add_argument('-m', '--matting_root', type=str,
                        help='root path of seg/matting images', default="sample_data/seg_orig")
    parser.add_argument('-s', '--csv_saved_path', type=str,
                        help='path to saved csv file', default="sample_data/filtered_data.csv")
    args = parser.parse_args()
    save_images(args.csv_saved_path, args.clip_root, args.matting_root)


if __name__ == '__main__':
    main()
