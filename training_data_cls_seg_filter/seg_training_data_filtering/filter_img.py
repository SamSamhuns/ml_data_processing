import numpy as np
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
            print("Exception in loading existing records", e)
            return
        good_cases = len([v[1] for v in seen.values() if v[1] == 1])
        print(f'Found {good_cases} good cases out of {len(seen)} total records')
    else:
        pd.DataFrame({}).to_csv(f, index=False)
        print('found 0 records')
    return seen


def gather_imgs(root_dir):
    for root, _, files in os.walk(root_dir):
        for f in sorted(files):
            yield os.path.join(root, f)


def alpha_blend(src, mask, mask_opacity):
    src = src.astype('float64')
    src *= (1.0 / src.max())
    mask = mask.astype('float64')
    mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    mask *= (1.0 / mask.max())
    return src * (1.0 - mask_opacity) + mask * mask_opacity


def append_to_file(seen: dict, f):
    res = ''.join([','.join([k, v[0], str(v[1])]) +
                   '\n' for k, v in seen.items()])
    with open(f, 'a+') as file:
        file.write(res)


def tag_images(f, clip_root, matting_root):
    seen_from_file = load_existing_records(f)
    seen = {}
    seen_clips, seen_mattings = [], []
    look_at = 0
    clip_collection = gather_imgs(clip_root)
    matting_collection = gather_imgs(matting_root)

    esc_pressed = False
    while True:
        if look_at >= len(seen_clips):
            while True:
                clip_path = next(clip_collection, None)
                matting_path = next(matting_collection, None)
                if clip_path not in seen_from_file:
                    break
        else:
            clip_path = seen_clips[look_at]
            matting_path = seen_mattings[look_at]
        if clip_path is None:
            break

        clip_img = cv2.imread(clip_path)
        try:
            mask = cv2.imread(matting_path, cv2.IMREAD_UNCHANGED)[:, :, 3]
        except Exception as e:
            mask = cv2.imread(matting_path, cv2.IMREAD_UNCHANGED)

        overlay_img = alpha_blend(clip_img, mask, 0.55)

        if clip_path in seen:
            if seen[clip_path][1] == 0:
                cv2.line(overlay_img, (100, 0), (0, 100), (0, 0, 255), 5)
                cv2.line(overlay_img, (0, 0), (100, 100), (0, 0, 255), 5)
            else:
                cv2.circle(overlay_img, (50, 50), 50, (0, 255, 0), 5)
        cv2.namedWindow('overlay', cv2.WINDOW_NORMAL)
        cv2.resizeWindow(
            'overlay', (clip_img.shape[1] // 1, clip_img.shape[0] // 1))
        cv2.imshow('overlay', overlay_img)
        press = cv2.waitKeyEx(0)
        if press == 27:
            append_to_file(seen, f)
            esc_pressed = True
            break
        elif press == 100:   # key d
            if clip_path not in seen:
                seen[clip_path] = (matting_path, 0)
                seen_clips.append(clip_path)
                seen_mattings.append(matting_path)
            look_at += 1
        elif press == 97:   # key a
            if clip_path not in seen:
                seen[clip_path] = (matting_path, 0)
                seen_clips.append(clip_path)
                seen_mattings.append(matting_path)
            look_at -= 1
            look_at = max(look_at, 0)
        elif press == 119:  # key w
            if clip_path not in seen:
                seen_clips.append(clip_path)
                seen_mattings.append(matting_path)
            seen[clip_path] = (matting_path, 1)
        else:
            if clip_path not in seen:  # key s
                seen_clips.append(clip_path)
                seen_mattings.append(matting_path)
            seen[clip_path] = (matting_path, 0)
        cv2.destroyAllWindows()
    if not esc_pressed:
        append_to_file(seen, f)


def main():
    parser = argparse.ArgumentParser(description='Image filtering')
    parser.add_argument('-c', '--clip_root', type=str,
                        help='root path of orig/clip images', default="sample_data/img_orig")
    parser.add_argument('-m', '--matting_root', type=str,
                        help='root path of seg/matting images', default="sample_data/seg_orig")
    parser.add_argument('-s', '--csv_save_path', type=str,
                        help='path to save csv file', default="sample_data/filtered_data.csv")
    args = parser.parse_args()
    tag_images(args.csv_save_path, args.clip_root, args.matting_root)


if __name__ == '__main__':
    main()
