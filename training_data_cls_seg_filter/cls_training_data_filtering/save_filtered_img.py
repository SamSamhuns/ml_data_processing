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
        good_cases = len([v for v in seen.values() if v[0] == 1])
        print(f'Found {good_cases} good cases out of {len(seen)} total records')
    else:
        pd.DataFrame({}).to_csv(f, index=False)
        print('found 0 records')
    return seen


def gather_imgs(root_dir):
    for root, _, files in os.walk(root_dir):
        for f in sorted(files):
            yield os.path.join(root, f)


def save_images(f, img_root):
    seen_from_file = load_existing_records(f)
    img_collection = gather_imgs(img_root)
    os.makedirs(img_root + '_OUT', exist_ok=True)

    i = 0
    for img_path in img_collection:
        img_path_base = os.path.basename(img_path)
        img_ok = True if seen_from_file[img_path][0] == 1 else False
        if img_ok:
            i += 1
            img = cv2.imread(img_path)
            cv2.imwrite(img_root + f'_OUT/{img_path_base}', img)
    print(i, f'images saved in {img_root}_OUT')


def main():
    parser = argparse.ArgumentParser(description='Image filtering')
    parser.add_argument('-c', '--img_root', type=str,
                        help='root path of orig images', default="sample_data/img_orig")
    parser.add_argument('-s', '--csv_saved_path', type=str,
                        help='path to saved csv file', default="sample_data/filtered_data.csv")
    args = parser.parse_args()
    save_images(args.csv_saved_path, args.img_root)


if __name__ == '__main__':
    main()
