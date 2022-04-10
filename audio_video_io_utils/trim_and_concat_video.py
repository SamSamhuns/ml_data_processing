import os
import shutil
import itertools
import os.path as osp
from pathlib import Path
from subprocess import Popen, PIPE
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import ffmpeg
import numpy as np


class ffmpegProcessor:

    __slots__ = ['cmd']

    def __init__(self, cmd="ffmpeg"):
        self.cmd = cmd

    def extract_audio(self, video_path, channels=1, sampling_rate=44100):
        try:
            out, err = (
                ffmpeg
                .input(video_path)
                .output('-', format='f32le', acodec='pcm_f32le', ac=channels, ar=f"{sampling_rate}")
                .run(cmd=self.cmd, capture_stdout=True, capture_stderr=True)
            )
        except Exception as e:
            print(e)
            raise
        return np.frombuffer(out, np.float32)


def extract_audio_arr(media_path, sr=44100, channels=1):
    """
    media_path: path to video/audio file
    sr: sampling rate equivalent to fps in videos, 44100 for top quality
    """
    fp = ffmpegProcessor()
    try:
        sound_arr = fp.extract_audio(
            media_path, channels=channels, sampling_rate=sr)
    except Exception as e:
        print(
            f"{e}. Could not load audio. Audio might be missing or corrupt in {media_path}.")
        return []
    return sound_arr


def ffmpeg_trim_subclip_and_concat(start_end_time_arr, video_path, target_path):
    """
    slow but accurate clip and concat, RECOMMENDED
    https://markheath.net/post/cut-and-concatenate-with-ffmpeg
    """
    se_arr = start_end_time_arr
    clen = len(se_arr)
    vcopy = f"[0:v]split = {clen}" + \
        ''.join([f"[vcopy{i}]" for i in range(1, clen + 1)]) + ", \n"
    acopy = f"[0:a]asplit = {clen}" + \
        ''.join([f"[acopy{i}]" for i in range(1, clen + 1)]) + ", \n"
    vtrim = ''.join([f"[vcopy{i}] trim={se_arr[i-1][0]}:{se_arr[i-1][1]},setpts=PTS-STARTPTS[v{i}], \n"
                     for i in range(1, clen + 1)])
    atrim = ''.join([f"[acopy{i}] atrim={se_arr[i-1][0]}:{se_arr[i-1][1]},asetpts=PTS-STARTPTS[a{i}], \n"
                     for i in range(1, clen + 1)])
    avconcat = ''.join([f"[v{i}] [a{i}] " for i in range(
        1, clen + 1)]) + f"concat=n={clen}:v=1:a=1[v][a]"

    av_combination = ''.join([vcopy, vtrim, acopy, atrim, avconcat])
    cmd = ["ffmpeg", "-y",
           "-i", video_path,
           "-filter_complex",
           f'{av_combination}',
           "-map", "[v]",
           "-map", "[a]",
           "-preset", "ultrafast",
           target_path]
    if os.path.exists(target_path):  # del pre-existing concatenated file
        os.remove(target_path)
    output, error = Popen(
        cmd, universal_newlines=True, stdout=PIPE, stderr=PIPE).communicate()
    if os.path.exists(target_path):
        print(f"Concatenated file created at {target_path}")
        return 0
    return -1


def ffmpeg_extract_subclip(inputfile, t1, t2, outputfile):
    cmd = ["ffmpeg", "-y",
           "-ss", "%0.2f" % t1,
           "-i", inputfile,
           "-t", "%0.2f" % (t2 - t1),
           "-map", "0",
           "-c", "copy",
           outputfile]
    output, error = Popen(
        cmd, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()


def ffmpeg_concat_subclips_with_transition(source_vid_path_list, target_vid_path, transition="fade", preset="ultrafast"):
    """
    # slower but adds transitions and accurate
    https://stackoverflow.com/questions/63553906/merging-multiple-video-files-with-ffmpeg-and-xfade-filter
    List of transition effects:
        custom, fade, wipeleft, wiperight, wipeup, wipedown, slideleft, slideright,
        slideup, slidedown, circlecrop, rectcrop, distance, fadeblack, fadewhite,
        radial, smoothleft, smoothright, smoothup, smoothdown, circleopen, circleclose,
        vertopen, vertclose, horzopen, horzclose, dissolve, pixelize, diagtl, diagtr,
        diagbl, diagbr, hlslice, hrslice, vuslice, vdslice, hblur, fadegrays, wipetl,
        wipetr, wipebl, wipebr, squeezeh, squeezev
    """
    if len(source_vid_path_list) == 1:
        shutil.copy(source_vid_path_list[0], target_vid_path)
        return

    def _gen_complex_xfade_filter(filepaths: list, transition: str):
        video_fades = ""
        audio_fades = ""
        settb = ""
        last_fade_output = "0:v"
        last_audio_output = "0:a"
        fade_duration = 0.30

        video_length = 0
        file_lengths = [0] * len(filepaths)

        for i in range(len(filepaths)):
            settb += "[%d]settb=AVTB[%d:v];" % (i, i)

        for i in range(len(filepaths) - 1):
            file_lengths[i] = float(ffmpeg.probe(
                filepaths[i])['format']['duration'])
            # video graph, chaining the efade operator
            video_length += file_lengths[i]
            next_fade_output = "v%d%d" % (i, i + 1)
            video_fades += f"[%s][%d:v]xfade=transition={transition}:duration=%f:offset=%f%s%s" % \
                (last_fade_output, i + 1, fade_duration, video_length - fade_duration * (i + 1),
                 '[' + next_fade_output +
                 '];' if (i) < len(filepaths) - 2 else "",
                 "" if (i) < len(filepaths) - 2 else ",format=yuv420p[video];")
            last_fade_output = next_fade_output

            # audio graph
            next_audio_output = "a%d%d" % (i, i + 1)
            audio_fades += "[%s][%d:a]acrossfade=d=%f%s" % \
                (last_audio_output, i + 1, fade_duration * 2,
                 '[' + next_audio_output + '];' if (i) < len(filepaths) - 2 else "[audio]")
            last_audio_output = next_audio_output

        return settb + video_fades + audio_fades

    files_input = [['-i', f] for f in source_vid_path_list]
    ffmpeg_args = ['ffmpeg',
                   *itertools.chain(*files_input),
                   '-filter_complex', _gen_complex_xfade_filter(
                       source_vid_path_list, transition),
                   '-preset', preset,
                   "-pix_fmt", "yuv420p",
                   '-map', '[video]',
                   '-map', '[audio]',
                   '-y',
                   target_vid_path]
    if os.path.exists(target_vid_path):  # del pre-existing concatenated file
        os.remove(target_vid_path)
    output, error = Popen(
        ffmpeg_args, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
    if os.path.exists(target_vid_path):
        print(f"Concatenated file created at {target_vid_path}")
        return 0
    return -1


def ffmpeg_extract_subclip_and_concat_with_transition_sequential(start_end_time_arr, src_video_path,
                                                                 target_video_path, transition="fade",
                                                                 preset="ultrafast", remove_subclips=False):
    """
    slow but accurate clip and concat, with transition
    """
    video_name = osp.basename(src_video_path).split('.')[0]
    clip_filenames = []
    target_video_dir = '/'.join(target_video_path.split('/')[:-1])
    for i, (start, end) in enumerate(start_end_time_arr):
        filename = f"{video_name}_highlight_" + \
            str(i + 1).zfill(5) + ".mp4"
        subclip_path = osp.join(target_video_dir, filename)
        clip_filenames.append(subclip_path)
        ffmpeg_extract_subclip(src_video_path, start,
                               end, outputfile=subclip_path)

    res = ffmpeg_concat_subclips_with_transition(
        clip_filenames, target_video_path, transition=transition, preset=preset)

    if remove_subclips:
        print(f"Removing all intermediate subclips from {target_video_path}")
        # remove clip files after concat except for the summarized video
        for fpath in Path(target_video_path).glob("*_highlight_*"):
            fpath.unlink()
    return res


def ffmpeg_extract_subclip_and_concat_with_transition(start_end_time_arr, src_video_path,
                                                      target_video_path, transition="fade",
                                                      preset="ultrafast", remove_subclips=False):
    """
    faster than sequetial and equally accurate clip and concat, with transition
    """
    video_name = osp.basename(src_video_path).split('.')[0]
    clip_filenames = []
    extract_clip_run_params = []
    target_video_dir = '/'.join(target_video_path.split('/')[:-1])
    for i, (start, end) in enumerate(start_end_time_arr):
        filename = f"{video_name}_highlight_" + \
            str(i + 1).zfill(5) + ".mp4"
        subclip_path = osp.join(target_video_dir, filename)
        clip_filenames.append(subclip_path)
        extract_clip_run_params.append(
            [src_video_path, start, end, subclip_path])

    with ThreadPoolExecutor(4) as executor:
        all_task = [executor.submit(ffmpeg_extract_subclip, *params)
                    for params in extract_clip_run_params]
        wait(all_task, return_when=ALL_COMPLETED)

    res = ffmpeg_concat_subclips_with_transition(
        clip_filenames, target_video_path, transition=transition, preset=preset)

    if remove_subclips:
        print(f"Removing all intermediate subclips from {target_video_path}")
        # remove clip files after concat except for the summarized video
        for fpath in Path(target_video_path).glob("*_highlight_*"):
            fpath.unlink()
    return res


# funcs below are for reference and not currently used
def ffmpeg_extract_subclip_half_resolution(inputfile, t1, t2, outputfile):
    """
    -preset <OPTIONS>
    faster means greater final video size

    ultrafast
    superfast
    veryfast
    faster
    fast
    medium – default preset
    slow
    slower
    veryslow
    """
    cmd = ["ffmpeg", "-y",
           "-ss", "%0.2f" % t1,
           "-i", inputfile,
           "-t", "%0.2f" % (t2 - t1),
           "-vf", "scale=iw/2:ih/2",
           "-preset", "medium",
           "-c:a", "copy",
           outputfile]
    output, error = Popen(
        cmd, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()


def ffmpeg_concat_subclip_from_file(concat_fname, targetname):
    # fast but inaccurate clip and concat, NOT RECOMMENDED
    cmd = ["ffmpeg", "-y",
           "-f", "concat",
           "-safe", "0",
           "-i", concat_fname,
           "-c", "copy",
           targetname]
    output, error = Popen(
        cmd, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()


def ffmpeg_extract_subclip_and_concat(start_end_time_arr, video_path, target_path, remove_subclips=True):
    # fast but inaccurate clip and concat, NOT RECOMMENDED
    video_name = osp.basename(video_path).split('.')[0]
    clip_filenames = []
    for i, (start, end) in enumerate(start_end_time_arr):
        filename = f"{video_name}_highlight_" + \
            str(i + 1).zfill(5) + ".mp4"
        clip_filenames.append(filename)
        ffmpeg_extract_subclip(
            video_path, start, end, outputfile=osp.join(target_path, filename))

    # concat after sub extraction
    concat_fname = osp.join(
        target_path, f"{video_name}_highlight_clips.txt")
    with open(concat_fname, 'w') as fw:
        [fw.write(f"file '{clip_path}' \n")
         for clip_path in clip_filenames]

    ffmpeg_concat_subclip_from_file(
        concat_fname, osp.join(target_path, f"summary_{video_name}.mp4"))

    if remove_subclips:
        print(f"Removing all intermediate subclips from {target_path}")
        # remove clip files after concat except for the summarized video
        for fpath in Path(target_path).glob("*_highlight_*"):
            fpath.unlink()


def main():
    from time import time
    src = "../datasets/soccer/orig_video/FULL MATCH - Barça 5-2 Mallorca (2019_2020)-mp4_1280x720.mp4"

    arr = [[1000, 1010], [1300, 1310], [1600, 1610], [2100, 2110],
           [2400, 2410], [3000, 3010], [3200, 3210], [4000, 4010]]
    tar = "target_media/conc_trans.mp4"
    t2 = time()
    # for i, (a, b) in enumerate(arr):
    #     ffmpeg_extract_subclip(src, a, b, f"target_media/slow_{i}.mp4")
    ffmpeg_extract_subclip_and_concat_with_transition(arr, src, tar)
    print(f"Conc Time taken {time()-t2:.3f}s")

    arr = [[1000, 1010], [1300, 1310], [1600, 1610], [2100, 2110],
           [2400, 2410], [3000, 3010], [3200, 3210], [4000, 4010]]
    tar = "target_media/seq_trans.mp4"
    t1 = time()
    # for i, (a, b) in enumerate(arr):
    #     ffmpeg_extract_subclip_fast(src, a, b, f"target_media/fast_{i}.mp4")
    ffmpeg_extract_subclip_and_concat_with_transition_sequential(arr, src, tar)
    print(f"Seq Time taken {time()-t1:.3f}s")


if __name__ == "__main__":
    main()
