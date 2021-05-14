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
            print(e, "Error in loading existing records")
            return
        good_cases = len([v for v in seen.values() if v[0] == 1])
        print(f'Found {good_cases} good cases out of {len(seen)} total records')
    else:
        print('found 0 records')
    return seen


def gather_imgs(root_dir):
    for root, _, files in os.walk(root_dir):
        for f in sorted(files):
            yield os.path.join(root, f)


def append_to_file(seen: dict, f):
    res = ''.join([','.join([k, str(v)]) +
                   '\n' for k, v in seen.items()])
    with open(f, 'a+') as file:
        file.write(res)


def tag_images(csv_save_path, img_root):
    seen_from_file = load_existing_records(csv_save_path)

    seen = {}
    seen_imgs = []
    look_at = 0

    imgs_collection = gather_imgs(img_root)
    esc_pressed = False

    while True:
        if look_at >= len(seen_imgs):
            while True:
                img_path = next(imgs_collection, None)
                if img_path not in seen_from_file:
                    break
        else:
            img_path = seen_imgs[look_at]
        if img_path is None:
            break

        img = cv2.imread(img_path)

        if img_path in seen:
            if seen[img_path] == 0:
                cv2.line(img, (100, 0), (0, 100), (0, 0, 255), 5)
                cv2.line(img, (0, 0), (100, 100), (0, 0, 255), 5)
            else:
                cv2.circle(img, (50, 50), 50, (0, 255, 0), 5)
        cv2.namedWindow('overlay', cv2.WINDOW_NORMAL)
        cv2.resizeWindow(
            img_path, (img.shape[1] // 1, img.shape[0] // 1))
        cv2.imshow(img_path, img)
        press = cv2.waitKeyEx(0)
        if press == 27:
            append_to_file(seen, csv_save_path)
            esc_pressed = True
            break
        elif press == 100:   # key d
            if img_path not in seen:
                seen[img_path] = (1)
                seen_imgs.append(img_path)
            look_at += 1
        elif press == 97:   # key a
            if img_path not in seen:
                seen[img_path] = (1)
                seen_imgs.append(img_path)
            look_at -= 1
            look_at = max(look_at, 0)
        elif press == 119:  # key w
            if img_path not in seen:
                seen_imgs.append(img_path)
            seen[img_path] = (1)
        else:
            if img_path not in seen:  # key s
                seen_imgs.append(img_path)
            seen[img_path] = (0)
        cv2.destroyAllWindows()
    if not esc_pressed:
        append_to_file(seen, csv_save_path)


def main():
    parser = argparse.ArgumentParser(description='Image filtering')
    parser.add_argument('-c', '--img_root', type=str,
                        help='root path of orig images', default="sample_data/img_orig")
    parser.add_argument('-s', '--csv_save_path', type=str,
                        help='path to save csv file', default="sample_data/filtered_data.csv")
    args = parser.parse_args()
    tag_images(args.csv_save_path, args.img_root)


if __name__ == '__main__':
    main()
