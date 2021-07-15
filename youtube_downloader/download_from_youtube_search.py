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
import csv
import os
import re

# min download speed in KiB/s
MIN_DOWNLOAD_SPEED = 300
# max number of download restarts
MAX_DOWNLOAD_RESTARTS = 50
# download unit MiB/s or KiB/s
DOWNLOAD_UNIT = "KiB/s"

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


class DownloadThrottleError(Exception):
    """Raised when download throttling is detected"""
    pass


def _my_hook(response):
    if "_speed_str" in response:
        speed_str = response["_speed_str"]
        if re.search(r"[0-9]+\.[0-9]+", speed_str):
            speed, unit = float(speed_str[:-5]), speed_str[-5:]
            if unit == "KiB/s" and speed < MIN_DOWNLOAD_SPEED:
                print(f"Speed is below {MIN_DOWNLOAD_SPEED} {unit}. Throttling possible. Exiting process and restarting download")
                raise DownloadThrottleError
    if response["status"] == "finished":
        global CURRENT_FILENAME
        CURRENT_FILENAME = response["filename"]
        print('Done downloading, now converting ...')


def download(search_str: str, options: dict):
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([search_str])


def load_video_search_opts_from_csv(csv_file):
    """
    csv file must have this 12 value fmt on any one given line with values inside double quotes:
        title: search_str, format, writeinfojson, metafromtitle, match_filter, matchtitle, \
                rejecttitle, dateafter, datebefore, max_filesize, min_filesize, max_downloads
        example: "soccer","mp4_640x360","True","None","None","None","None","20121026","None","300m","5m","10"
    Unused settings should be set to "None"
    reference: https://github.com/ytdl-org/youtube-dl/blob/f19eae429a2c999db143060fded506dc52aaa398/youtube_dl/options.py#L144

    """
    video_info_list = []
    with open(csv_file, 'r') as f_csv:
        _ = f_csv.readline()  # header
        for line in csv.reader(f_csv, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True):
            if len(line) != 12:
                print(
                    f"Full config absent in line {line}. Need 13 vals in double quotes(\"\") sep by ,")
                continue
            line = [data.strip() for data in line]
            (search_str, format, writeinfojson, metafromtitle, match_filter, matchtitle,
                rejecttitle, dateafter, datebefore, max_filesize, min_filesize, max_downloads) = line
            video_info_list.append([search_str, format, writeinfojson, metafromtitle, match_filter, matchtitle,
                                    rejecttitle, dateafter, datebefore, max_filesize, min_filesize, max_downloads])
    return video_info_list


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--title_csv', type=str,
                        default="search_keywords/soccer_keyword.csv",
                        help="csv file with reuired fmt")
    parser.add_argument('-v', '--download_dir', type=str,
                        default="datasets/soccer/orig_video_searched",
                        help="directory where videos are downloaded to. " +
                        "Created automatically if it doesnt alr exist")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    download_list = load_video_search_opts_from_csv(args.title_csv)
    os.makedirs(args.download_dir, exist_ok=True)

    # add format and outtmpl later
    ydl_opts = {"progress_hooks": [_my_hook],
                # the below passed through csv file
                "search_str": None,
                "writeinfojson": True,
                "metafromtitle": None,
                "match_filter": None,
                "matchtitle": None,     # like re.search regex='(dog|cat)'
                "rejecttitle": None,    # like re.search regex='(mouse|horse)'
                "dateafter": None,      # 20130201
                "datebefore": None,     # 20131026
                "max_filesize": None,   # 50K or 44.6M, actual val in bytes
                "min_filesize": None,   # 50K or 44.6M,  actual val in bytes
                "max_downloads": None}  # int
    '''
    metafromtitle
     help='Parse additional metadata like song title / artist from the video title. '
             'The format syntax is the same as --output. Regular expression with '
             'named capture groups may also be used. '
             'The parsed parameters replace existing values. '
             'Example: --metadata-from-title "%(artist)s - %(title)s" matches a title like '
             '"Coldplay - Paradise". '
             'Example (regex): --metadata-from-title "(?P<artist>.+?) - (?P<title>.+)"')

    match_filter
    help=(
            'Generic video filter. '
            'Specify any key (see the "OUTPUT TEMPLATE" for a list of available keys) to '
            'match if the key is present, '
            '!key to check if the key is not present, '
            'key > NUMBER (like "comment_count > 12", also works with '
            '>=, <, <=, !=, =) to compare against a number, '
            'key = \'LITERAL\' (like "uploader = \'Mike Smith\'", also works with !=) '
            'to match against a string literal '
            'and & to require multiple matches. '
            'Values which are not known are excluded unless you '
            'put a question mark (?) after the operator. '
            'For example, to only match videos that have been liked more than '
            '100 times and disliked less than 50 times (or the dislike '
            'functionality is not available at the given service), but who '
            'also have a description, use --match-filter '
            '"like_count > 100 & dislike_count <? 50 & description" .'
        ))
    '''
    for (search_str, format, writeinfojson, metafromtitle, match_filter, matchtitle,
            rejecttitle, dateafter, datebefore, max_filesize, min_filesize, max_downloads) in download_list:
        fmt = YL_FMT_DICT[format]
        size_mult_dict = {'K': 1024, 'M': 1048576}
        try:
            if max_downloads is None:
                print(
                    f"Max download fo value {max_downloads} is not allowed. Set a number i.e. 1000")
                continue
            ydl_opts["format"] = fmt
            ydl_opts["outtmpl"] = os.path.join(
                args.download_dir, f'%(title)s-{format}.%(ext)s')

            ydl_opts["writeinfojson"] = writeinfojson
            ydl_opts["metafromtitle"] = metafromtitle
            ydl_opts["match_filter"] = match_filter
            ydl_opts["matchtitle"] = matchtitle
            ydl_opts["rejecttitle"] = rejecttitle
            ydl_opts["dateafter"] = dateafter
            ydl_opts["datebefore"] = datebefore
            ydl_opts["max_filesize"] = int(
                max_filesize[:-1]) * size_mult_dict[max_filesize[-1].upper()]
            ydl_opts["min_filesize"] = int(
                min_filesize[:-1]) * size_mult_dict[min_filesize[-1].upper()]
            ydl_opts["max_downloads"] = int(max_downloads)
            ydl_opts["default_search"] = f"ytsearch{int(max_downloads)}"

            # for avoiding youtube throtling
            ydl_opts['socket_timeout'] = 1
            ydl_opts['retries'] = 1000
            ydl_opts["external_downloader"] = "aria2c"

            ydl_opts = {k: v if v != "None" else None
                        for k, v in ydl_opts.items()}
            print("Downloading with options", ydl_opts)

            # for avoiding youtube throtling
            download_complete = False
            i = 0
            while not download_complete:
                try:
                    download(search_str, ydl_opts)
                    download_complete = True
                except DownloadThrottleError:
                    print("Restarting download")
                if i > MAX_DOWNLOAD_RESTARTS:
                    print(f"Aborting. Max restarts exceeded {MAX_DOWNLOAD_RESTARTS}")
                    print("Increase max_download_restarts for increased download restart tries")
                    break
                i += 1
        except youtube_dl.utils.DownloadError:
            print(
                f'download error: metafromtitle:{metafromtitle}, match_filter:{match_filter} matchtitle:{matchtitle} | {format}')


if __name__ == "__main__":
    main()
