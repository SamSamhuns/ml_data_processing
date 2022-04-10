"""
Count the quartile and average lengths of video files recursively inside a directory
"""
import glob
import time
import argparse
import multiprocessing
from typing import List

import cv2
import numpy as np


def get_video_len(fpath) -> float:
    try:
        cap = cv2.VideoCapture(fpath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        video_len = frame_count / fps
        cap.release()
    except Exception as e:
        print(e)
        return 0
    return video_len


def get_video_length_statistics(video_lengths: List[float], npy_spath="video_lengths.npy") -> None:
    """
    Print and save video length statistics given array of video lengths
    """
    # drop videos that were not processed properly
    video_lengths = [length for length in video_lengths if length > 0]
    n = len(video_lengths)
    if n == 0:
        return
    video_lengths.sort()
    first_quartile = (n + 1) // 4
    second_quartile = (n + 1) // 2
    third_quartile = (3 * (n + 1)) // 4

    print(f"\tMin           = {video_lengths[0]}s")
    print(f"\t25th Q        = {video_lengths[first_quartile]:.3f}s")
    print(f"\t50th Q/Median = {video_lengths[second_quartile]:.3f}s")
    print(f"\tAverage       = {sum(video_lengths)/n:.3f}s")
    print(f"\t75th Q        = {video_lengths[third_quartile]:.3f}s")
    print(f"\tMax           = {video_lengths[-1]}s")
    np.save(npy_spath, np.asarray(video_lengths))


def single_process_count(root_dir: str, ext: str = "mp4") -> None:
    print("\nSingle-process counting video length statistics")
    t1 = time.time()
    video_lengths = [get_video_len(fpath)
                     for fpath in glob.glob(f"{root_dir}/**/*.{ext}", recursive=True)]
    get_video_length_statistics(video_lengths)
    print(
        f"Processing time for {len(video_lengths)} videos {time.time()-t1:.2f}s")


def multi_process_count(root_dir: str, ext: str = "mp4") -> None:
    def _get_multi_process_length(root_dir, ext="mp4"):
        pool = multiprocessing.Pool()
        video_paths = [fpath for fpath in glob.glob(
            f"{root_dir}/**/*.{ext}", recursive=True)]

        results = pool.map(get_video_len, video_paths)
        pool.close()
        pool.join()
        return results

    print("\nMulti-process counting video length statistics")
    t1 = time.time()
    video_lengths = _get_multi_process_length(root_dir, ext)
    get_video_length_statistics(video_lengths)
    print(
        f"Processing time for {len(video_lengths)} videos {time.time()-t1:.2f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Get statistics on video length of videos inside a directory")
    parser.add_argument("-s", "--source_dir",
                        required=True,
                        help='Path to source dir.')
    parser.add_argument("-e", "--extension",
                        default="mp4",
                        help="Video file extensions to be considered. (default: %(default)s)")
    args = parser.parse_args()
    multi_process_count(args.source_dir, args.extension)
