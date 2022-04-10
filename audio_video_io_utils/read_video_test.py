import av
import cv2
import sys
import time
import ffmpeg
import numpy as np
from queue import Queue
from threading import Thread

from decord import cpu
from decord import VideoReader, VideoLoader


"""
import multiprocessing as mp


def load_video_cv2_mproc(inputfile):

    def process_video_multiprocessing(group_number):
        # Read video file
        cap = cv2.VideoCapture(inputfile)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_jump_unit * group_number)

        proc_frames = 0
        arr = []
        try:
            while proc_frames < frame_jump_unit:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.resize(frame, (800, 600))
                arr.append(frame)
                proc_frames += 1
        except Exception:
            cap.release()

        cap.release()
        return proc_frames, arr

    def multi_process(num_processes):
        print("Video processing using {} processes...".format(num_processes))
        # Parallelize the execution of a function across multiple input values
        p = mp.Pool(num_processes)
        p.map(process_video_multiprocessing, range(num_processes))
        print([f[0] for f in arr])
        return arr

    t1 = time.time()
    p = ffmpeg.probe(inputfile, select_streams='v')
    num_processes = 4  # mp.cpu_count()
    frames = int(p['streams'][0]['nb_frames'])
    frame_jump_unit = frames // num_processes
    print(frames, num_processes)
    print("Number of CPU: " + str(num_processes))
    arr = multi_process(num_processes)
    print("CV2 multi-proc:")
    print(f"\t Output shape: {np.array(arr).shape}")
    print(f"\t Time: {time.time() - t1:.2f} s")"""


def load_video_decord_batched(inputfile):
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
    vl = VideoLoader([inputfile], ctx=[cpu(0)], shape=(
        10, 600, 800, 3), interval=0, skip=0, shuffle=1)
    print('Total batches:', len(vl))

    arr = []
    for batch in vl:
        arr.append(batch[0].asnumpy())
    arr = np.array(arr)
    arr = arr.reshape(-1, 600, 800, 3)
    return arr


def load_video_decord_index(inputfile):
    """Useful for loading entire video in memory & skipping frames
    CPU will overload if frame length exceeds 2000 frames
    """
    t1 = time.time()
    vr = VideoReader(inputfile, ctx=cpu(0))
    vid_len = len(vr)
    # To get multiple frames at once, use get_batch
    # duplicate frame indices will be accepted and handled internally to avoid duplicate decoding
    arr = vr.get_batch([f for f in range(vid_len)]).asnumpy()

    print("Decord Batched:")
    print(f"\t Output shape: {np.array(arr).shape}")
    print(f"\t Time: {time.time() - t1:.2f} s")


def load_video_decord_seq(inputfile):
    t1 = time.time()
    vr = VideoReader(inputfile, ctx=cpu(0), width=800, height=600)
    arr = []

    # # 1. the simplest way is to directly access frames
    for i in range(len(vr)):
        # the video reader will handle seeking and skipping in the most efficient manner
        frame = vr[i]
        arr.append(frame.asnumpy())

    print("Decord Seq:")
    print(f"\t Output shape: {np.array(arr).shape}")
    print(f"\t Time: {time.time() - t1:.2f} s")


def load_video_cv2_mthread(inputfile):

    class FileVideoStream:
        def __init__(self, path, transform=None, queue_size=128):
            """Class to create separate thread to read frames from video
            """
            self.stream = cv2.VideoCapture(path)
            self.thread_stopped = False
            self.transform = transform

            # init the queue used to store frames read from the video file
            self.Q = Queue(maxsize=queue_size)
            # init thread
            self.thread = Thread(target=self.update, args=())
            self.thread.daemon = True

        def start(self):
            # start a thread to read frames from the file video stream
            self.thread.start()
            return self

        def update(self):
            # keep looping infinitely
            while True:
                if self.thread_stopped:
                    break
                # ensure the queue has room in it
                if not self.Q.full():
                    # read the next frame from the file
                    (grabbed, frame) = self.stream.read()

                    # if the `grabbed` boolean is `False`, then we have
                    # reached the end of the video file
                    if not grabbed:
                        self.thread_stopped = True

                    # if there are transforms to be done, might as well
                    # do them on producer thread before handing back to
                    # consumer thread. ie. Usually the producer is so far
                    # ahead of consumer that we have time to spare.
                    #
                    # Python is not parallel but the transform operations
                    # are usually OpenCV native so release the GIL.
                    #
                    # Really just trying to avoid spinning up additional
                    # native threads and overheads of additional
                    # producer/consumer queues since this one was generally
                    # idle grabbing frames.
                    if self.transform:
                        frame = self.transform(frame)

                    # add the frame to the queue
                    self.Q.put(frame)
                else:
                    time.sleep(0.01)  # Rest for 10ms, we have a full queue

            self.stream.release()

        def read(self):
            # return next frame in the queue
            return self.Q.get(block=True, timeout=2.0)

        # Insufficient to have consumer use while(more()) which does
        # not take into account if the producer has reached end of
        # file stream.
        def running(self):
            return self.more() or not self.thread_stopped

        def more(self):
            # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
            tries = 0
            while self.Q.qsize() == 0 and not self.thread_stopped and tries < 5:
                # time.sleep(0.009)
                tries += 1

            return self.Q.qsize() > 0

        def stop(self):
            # indicate that the thread should be stopped
            self.thread_stopped = True
            # wait until stream resources are released (producer thread might be still grabbing frame)
            self.thread.join()

    t1 = time.time()
    fvs = FileVideoStream(inputfile, queue_size=1024).start()
    arr = []
    while fvs.running():
        frame = fvs.read()
        if frame is not None:
            frame = cv2.resize(frame, (800, 600))
            arr.append(frame)

    cv2.destroyAllWindows()
    fvs.stop()
    print("CV2 multi-thread:")
    print(f"\t Output shape: {np.array(arr).shape}")
    print(f"\t Time: {time.time() - t1:.2f} s")


def disp_video_cv2_mthread_v2(inputfile):
    """
    Faster than single thread for video/webcam disp
    Highly recommended for webcam use over single thread cv
    """
    class VideoStreamWidget(object):
        def __init__(self, src=0):
            self.capture = cv2.VideoCapture(src)
            # Start the thread to read frames from the video stream
            self.thread = Thread(target=self.update, args=())
            self.thread.daemon = True
            self.thread.start()

        def update(self):
            # Read the next frame from the stream in a different thread
            while True:
                if self.capture.isOpened():
                    (self.status, self.frame) = self.capture.read()
                time.sleep(.01)

        def show_frame(self):
            # Display frames in main program
            cv2.imshow('frame', self.frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                self.capture.release()
                cv2.destroyAllWindows()
                exit(1)

    def single_thread_cam(src=0):
        cap = cv2.VideoCapture(src)
        while True:
            try:
                t1 = time.time()
                status, frame = cap.read()
                cv2.imshow('frame', frame)
                key = cv2.waitKey(1)
                if key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    exit(1)
                print(f"FPS: {1/(time.time()-t1):.2f}")
            except AttributeError:
                pass

    def multi_thread_cam(src=0):
        video_stream_widget = VideoStreamWidget(src)
        while True:
            try:
                t1 = time.time()
                video_stream_widget.show_frame()
                print(f"FPS: {1/(time.time()-t1):.2f}")
            except AttributeError:
                pass

    t1 = time.time()
    multi_thread_cam(inputfile)

    cv2.destroyAllWindows()
    print("CV2 multi-thread v2:")
    print(f"\t Time: {time.time() - t1:.2f} s")


def load_video_ffmpeg(inputfile):
    t1 = time.time()
    """
    # Use ffprobe to get video frames resolution
    p = ffmpeg.probe(inputfile, select_streams='v')
    vstream = p['streams'][0]
    width, height = vstream['width'], vstream['height']
    duration_sec = vstream['duration']
    frames = vstream['nb_frames']
    r_fr = vstream["r_frame_rate"].split('/')
    fps = np.ceil(int(r_fr[0]) / int(r_fr[1]))
    print(
        f"Video duration is {duration_sec} secs with {frames} frames and {fps} fps")
    """

    width, height = 800, 600
    # Stream the entire video as one large array of bytes
    out, _ = (
        ffmpeg
        .input(inputfile)
        .filter('scale', width, height)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24',
                **{'preset': "ultrafast"},
                **{"loglevel": "error"})
        .run(capture_stdout=True)
    )
    arr = (
        np
        .frombuffer(out, np.uint8)
        .reshape([-1, height, width, 3])
    )
    print("ffmpeg:")
    print(f"\t Output shape: {arr.shape}")
    print(f"\t Time: {time.time() - t1:.2f} s")


def load_video_cv2(inputfile):
    t1 = time.time()
    cap = cv2.VideoCapture(inputfile)
    arr = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (800, 600))
        arr.append(frame)
    cap.release()
    cv2.destroyAllWindows()
    print("OpenCV:")
    print(f"\t Output shape: {np.array(arr).shape}")
    print(f"\t Time: {time.time() - t1:.2f} s")


def load_video_pyav(inputfile):
    t1 = time.time()
    arr = []
    container = av.open(inputfile)
    container.streams.video[0].thread_type = 'AUTO'  # Go faster!
    for frame in container.decode(video=0):
        frame = frame.to_ndarray(format='rgb24')
        frame = cv2.resize(frame, (800, 600))
        arr.append(frame)
    container.close()
    print("PyAV:")
    print(f"\t Output shape: {np.array(arr).shape}")
    print(f"\t Time: {time.time() - t1:.2f} s")


def main():
    load_video_decord_seq(sys.argv[1])
    load_video_decord_index(sys.argv[1])
    load_video_cv2_mthread(sys.argv[1])
    load_video_cv2(sys.argv[1])
    load_video_pyav(sys.argv[1])
    load_video_ffmpeg(sys.argv[1])


if __name__ == "__main__":
    main()
