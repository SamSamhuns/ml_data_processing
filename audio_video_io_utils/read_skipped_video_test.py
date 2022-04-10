import av
import cv2
import time
import numpy as np
from vidgear.gears import CamGear

import os
# uncomment below increase DECORD read retry attempts
# os.environ['DECORD_EOF_RETRY_MAX'] = "20480"
from decord import cpu
from decord import VideoReader, VideoLoader


def get_frame(cap, index):
    if cap.isOpened():
        if hasattr(cv2, 'cv'):
            cap.set(cv2.cv.CAP_PROP_POS_FRAMES, index)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = cap.read()
        if not ret:
            return None
        return frame
    return None


def get_img_list_opencv_seek(video_filename, MAX_N_FRAME=300, reshape_size=(299, 299)):
    start = time.time()
    cap = cv2.VideoCapture(video_filename)
    step = fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
    nframes = np.floor(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"OpenCV Seek: FPS={fps}, num frames={nframes}")
    img_list = []
    i = 0
    save_frames_num = 0
    while cap.isOpened():
        i += 1
        if i % step == 0 or i == 1:
            frame = get_frame(cap, i - 1)
            if frame is None:
                break
            img = frame[..., ::-1]  # BGR2RGB
            save_frames_num += 1
            if save_frames_num > MAX_N_FRAME:
                break
            img = cv2.resize(img, reshape_size).astype(np.float32)
            img_list.append(img)
    cap.release()
    cv2.destroyAllWindows()
    del cap
    elapsed_time = time.time() - start
    return np.array(img_list), elapsed_time


def get_img_list_opencv_seq(video_filename, MAX_N_FRAME=300, reshape_size=(299, 299)):
    start = time.time()
    cap = cv2.VideoCapture(video_filename)
    step = fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
    nframes = np.floor(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"OpenCV Seq: FPS={fps}, num frames={nframes}")
    img_list = []
    i = 0
    save_frames_num = 0
    ret, frame = cap.read()
    while ret:
        i += 1
        if i % step == 0 or i == 1:
            img = frame[..., ::-1]  # BGR2RGB
            save_frames_num += 1
            if save_frames_num > MAX_N_FRAME:
                break
            img = cv2.resize(img, reshape_size).astype(np.float32)
            img_list.append(img)
        ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()
    del cap
    elapsed_time = time.time() - start
    return np.array(img_list), elapsed_time


def get_img_list_reader_av(video_filename, MAX_N_FRAME=300, reshape_size=(299, 299)):
    start = time.time()
    cap = av.open(video_filename)
    cap.streams.video[0].thread_type = 'AUTO'
    step = fps = int(round(cap.streams.video[0].average_rate))
    nframes = np.floor(cap.streams.video[0].frames)
    print(f"PyAV Seq: FPS={fps}, num frames={nframes}")
    img_list = []
    i = 0
    save_frames_num = 0
    for frame in cap.decode(video=0):
        i += 1
        if i % step == 0 or i == 1:
            img = np.array(frame.to_image())
            save_frames_num += 1
            if save_frames_num > MAX_N_FRAME:
                break
            img = cv2.resize(img, reshape_size).astype(np.float32)
            img_list.append(img)
    cap.close()
    del cap
    elapsed_time = time.time() - start
    return np.array(img_list), elapsed_time


def get_img_list_vidgear_seq(video_filename, MAX_N_FRAME=300, reshape_size=(299, 299)):
    start = time.time()
    stream = CamGear(source=video_filename).start()
    step = fps = int(stream.stream.get(cv2.CAP_PROP_FPS))
    nframes = np.floor(stream.stream.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"VidGears Seq: FPS={fps}, num frames={nframes}")
    img_list = []
    i = 0
    save_frames_num = 0
    while i < nframes:
        i += 1
        frame = stream.read()
        if frame is None:
            break
        if i % step == 0 or i == 1:
            save_frames_num += 1
            if save_frames_num > MAX_N_FRAME:
                break
            img = cv2.resize(frame, reshape_size).astype(np.float32)
            img_list.append(img)
    stream.stop()
    elapsed_time = time.time() - start
    return np.array(img_list), elapsed_time


def get_img_list_decord_batched(video_filename, MAX_N_FRAME=300, reshape_size=(299, 299)):
    """Useful for skipping frames
    interval : int
        Intra-batch frame interval.
        Higher means frames in a batch are farther apart in time
        Larger value means less frames taken from video
    skip : int
        Inter-batch frame interval.
        Num of frames to skip between batches
        Larger value means less frames taken from video
    shuffle : int
        Shuffling strategy. Can be
        `0`:  all sequential, no seeking, following initial filename order
        `1`:  random filename order, no random access for each video, very efficient
        `2`:  random order
        `3`:  random frame access in each video only.
    """
    start = time.time()
    width, height = reshape_size
    cap = cv2.VideoCapture(video_filename)
    batch = 32
    step = fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
    cap.release()
    vl = VideoLoader([video_filename], ctx=[cpu(0)], shape=(
        batch, height, width, 3), interval=step, skip=0, shuffle=1)
    print(
        f"Decord Batched: FPS={fps}, num frames={len(vl)} * {batch} = {len(vl) * batch}")

    arr = []
    for batch in vl:
        arr.append(batch[0].asnumpy())
    arr = np.array(arr)
    arr = arr.reshape(-1, height, width, 3)

    elapsed_time = time.time() - start
    return arr, elapsed_time


def get_img_list_decord_index(video_filename, MAX_N_FRAME=300, reshape_size=(299, 299)):
    """Useful for loading entire video in memory & skipping frames
    CPU will overload if frame length exceeds 2000 frames
    """
    start = time.time()
    width, height = reshape_size
    vr = VideoReader(video_filename, ctx=cpu(0), width=width, height=height)
    step = fps = int(vr.get_avg_fps())
    vid_len = len(vr)
    print(f"Decord Indexed: FPS={fps}, num frames={vid_len}")
    index_list = [i for i in range(vid_len) if i % step == 0][:MAX_N_FRAME]
    # To get multiple frames at once, use get_batch
    # duplicate frame indices will be accepted and handled internally to avoid duplicate decoding
    arr = vr.get_batch(index_list).asnumpy()

    elapsed_time = time.time() - start
    return arr, elapsed_time


def get_img_list_decord_seq(video_filename, MAX_N_FRAME=300, reshape_size=(299, 299)):
    t1 = time.time()
    width, height = reshape_size
    vr = VideoReader(video_filename, ctx=cpu(0), width=width, height=height)
    step = fps = int(vr.get_avg_fps())
    print(f"Decord Seq: FPS={fps}, num frames={len(vr)}")
    arr = []
    save_frames_num = 0
    # # 1. the simplest way is to directly access frames
    for i in range(len(vr)):
        if save_frames_num > MAX_N_FRAME:
            break
        if i % step == 0 or i == 1:
            # the video reader will handle seeking and skipping in the most efficient manner
            frame = vr[i]
            arr.append(frame.asnumpy())
            save_frames_num += 1

    elapsed_time = time.time() - t1
    return np.array(arr), elapsed_time


def main():
    video_filename = "messi.mp4"

    img_arr, etime = get_img_list_vidgear_seq(
        video_filename, MAX_N_FRAME=300, reshape_size=(299, 299))
    print("\tVidGears Seq:", img_arr.shape, etime)

    img_arr, etime = get_img_list_opencv_seek(
        video_filename, MAX_N_FRAME=300, reshape_size=(299, 299))
    print("\tOpenCV seek:", img_arr.shape, etime)

    img_arr, etime = get_img_list_opencv_seq(
        video_filename, MAX_N_FRAME=300, reshape_size=(299, 299))
    print("\tOpenCV sequential:", img_arr.shape, etime)

    img_arr, etime = get_img_list_reader_av(
        video_filename, MAX_N_FRAME=300, reshape_size=(299, 299))
    print("\tPyAV Seq:", img_arr.shape, etime)

    img_arr, etime = get_img_list_decord_seq(
        video_filename, MAX_N_FRAME=300, reshape_size=(299, 299))
    print("\tDecord Seq:", img_arr.shape, etime)

    img_arr, etime = get_img_list_decord_index(
        video_filename, MAX_N_FRAME=300, reshape_size=(299, 299))
    print("\tDecord Indexed:", img_arr.shape, etime)

    img_arr, etime = get_img_list_decord_batched(
        video_filename, MAX_N_FRAME=300, reshape_size=(299, 299))
    print("\tDecord Batched:", img_arr.shape, etime)


if __name__ == "__main__":
    main()
