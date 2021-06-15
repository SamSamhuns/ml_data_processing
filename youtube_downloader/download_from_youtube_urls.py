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
22          mp4       1280x720    (best)
"""

from __future__ import unicode_literals
import youtube_dl
import argparse
import os


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
    "mp4_1280x720": '22'
}


def _my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def download(url: str, options: dict):
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])


def load_video_urls_from_csv(csv_file):
    """
    csv file must have fmt on any one given line:
        channel, format, lang, yt_title, yt_url
    """
    video_info_list = []
    with open(csv_file, 'r') as f_csv:
        _ = f_csv.readline()  # header
        for line in f_csv:
            line = line.strip().split(',')
            line = [data.strip() for data in line]
            channel, format, lang, yt_title, yt_url = line
            if type is None:
                print(f"Type {type} does not exist for video {yt_title} at {yt_url}")
                continue
            video_info_list.append([channel, format, lang, yt_title, yt_url])
    return video_info_list


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url_csv', type=str,
                        default="soccer_fullmatch.csv",
                        help="csv file with channel,format,lang,yt_title,yt_url vals")
    parser.add_argument('-v', '--download_dir', type=str,
                        default="../datasets/soccer/orig_video",
                        help="directory where videos are downloaded to. " +
                        "Created automatically if it doesnt alr exist")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    download_list = load_video_urls_from_csv(args.url_csv)
    os.makedirs(args.download_dir, exist_ok=True)

    # add format and outtmpl later
    ydl_opts = {"progress_hooks": [_my_hook]}

    for channel, format, lang, yt_title, yt_url in download_list:
        fmt = YL_FMT_DICT[format]
        try:
            ydl_opts["format"] = fmt
            ydl_opts["outtmpl"] = os.path.join(args.download_dir, f'%(title)s-{format}.%(ext)s')
            download(yt_url, ydl_opts)
        except youtube_dl.utils.DownloadError:
            print(f'download error: {yt_url} | {format}')


if __name__ == "__main__":
    main()
