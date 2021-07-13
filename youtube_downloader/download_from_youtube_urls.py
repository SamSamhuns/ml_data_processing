"""
install youtube_dl in a virtual env with `pip install --upgrade youtube_dl` first
fmt_code   extension  resolution  note
140         m4a       audio only  DASH audio , audio@128k (worst)
160         mp4       144p        DASH video , video only
133         mp4       240p        DASH video , video only
134         mp4       360p        DASH video , video only
135         mp4       480p        DASH video , video only
136         mp4       720p        DASH video , video only
17          3gp       176x144
36          3gp       320x240
5           flv       400x240
43          webm      640x360
18          mp4       640x360
135+140     mp4+m4a   853x480
22          mp4       1280x720    (best)
"""

from __future__ import unicode_literals
import youtube_dl
import subprocess
import argparse
import os
import re

# min download speed in KiB/s
MIN_DOWNLOAD_SPEED = 200

YL_FMT_DICT = {
    "m4a": '140',
    "mp4_144p": '160',
    "mp4_240p": '133',
    "mp4_360p": '134',
    "mp4_480p": '135',
    "mp4_720p": '136',
    "mp4_1080p": '137',
    "gp3_176x144": '17',
    "gp3_320x240": '36',
    "flv": '5',
    "webm": '43',
    "mp4_640x360": '18',
    "mp4_853x480": '135+140',
    "mp4_1280x720": '22'
}


def _my_hook(response):
    if "_speed_str" in response:
        speed_str = response["_speed_str"]
        if re.search(r"[0-9]+\.[0-9]+", speed_str):
            speed, unit = float(speed_str[:-5]), speed_str[-5:]
            if unit == "KiB/s" and speed < MIN_DOWNLOAD_SPEED:
                print(f"Speed is below {MIN_DOWNLOAD_SPEED} {unit}. Throttling possible. Exiting process and restarting download")
                exit(2)
    if response["status"] == "finished":
        global CURRENT_FILENAME
        CURRENT_FILENAME = response["filename"]
        print('Done downloading, now converting ...')


def ffmpeg_extract_subclip(input_video, t1, t2, output_video):
    cmd = ["ffmpeg", "-y",
           "-ss", t1,
           "-i", input_video,
           "-t", t2,
           "-map", "0",
           "-c", "copy",
           output_video]
    output, error = subprocess.Popen(
        cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


def download(url: str, options: dict):
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])


def load_video_urls_from_csv(csv_file):
    """
    csv file must have this fmt on any one given line:
        channel, format, lang, yt_title, yt_url, max_length(HH:MM:SS)
    """
    video_info_list = []
    with open(csv_file, 'r') as f_csv:
        _ = f_csv.readline()  # header
        for line in f_csv:
            if line[0] == '#':
                continue  # skip comments
            line = line.strip().split(',')
            line = [data.strip() for data in line]
            channel, format, lang, yt_title, yt_url, max_length = line
            if type is None:
                print(
                    f"Type {type} does not exist for video {yt_title} at {yt_url}")
                continue
            video_info_list.append(
                [channel, format, lang, yt_title, yt_url, max_length])
    return video_info_list


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url_csv', type=str,
                        default="urls/soccer_fullmatch.csv",
                        help="csv file with channel,format,lang,yt_title,yt_url vals")
    parser.add_argument('-v', '--download_dir', type=str,
                        default="../datasets/soccer/orig_video",
                        help="directory where videos are downloaded to. " +
                        "Created automatically if it doesnt alr exist")
    parser.add_argument('-r', '--force_res', type=str,
                        help="Overrrides the resolution value in csv. " +
                             "Enter a valid resolution value in form mp4_640x360/mp4_853x480/mp4_1280x720")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    download_list = load_video_urls_from_csv(args.url_csv)
    os.makedirs(args.download_dir, exist_ok=True)

    # add format and outtmpl later
    ydl_opts = {"progress_hooks": [_my_hook]}
    time_fmt = re.compile(r"^\d{2}:[0-5][0-9]:[0-5][0-9]$")

    for channel, format, lang, yt_title, yt_url, max_length in download_list:
        format = format if args.force_res is None else args.force_res
        fmt = YL_FMT_DICT[format]
        try:
            ydl_opts["format"] = fmt
            ydl_opts["outtmpl"] = os.path.join(
                args.download_dir, f'%(title)s-{format}.%(ext)s')
            # for avoiding youtube throtling
            ydl_opts['retries'] = 5000
            ydl_opts['socket_timeout'] = 1
            ydl_opts["external_downloader"] = "aria2c"
            download(yt_url, ydl_opts)

            if max_length == "-1":  # no video trimming, use full orig length
                continue
            if not time_fmt.match(max_length):
                print(
                    f"max_length fmt must be a valid HH:MM:SS not {max_length}")
                continue

            try:
                trim_basename = "temp_trim_" + os.path.basename(CURRENT_FILENAME)
                trim_video_save_path = os.path.join(
                    args.download_dir, trim_basename)
                ffmpeg_extract_subclip(
                    CURRENT_FILENAME, "00:00:00", max_length, trim_video_save_path)

                os.remove(CURRENT_FILENAME)
                os.rename(trim_video_save_path, CURRENT_FILENAME)
            except Exception as e:
                print(e, f"Skipping {yt_title}")

        except youtube_dl.utils.DownloadError:
            print(f'download error: {yt_url} | {format}')


if __name__ == "__main__":
    main()
