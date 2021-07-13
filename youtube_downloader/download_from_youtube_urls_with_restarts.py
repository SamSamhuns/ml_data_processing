from __future__ import unicode_literals
from subprocess import call
import argparse


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
    parser.add_argument('-m', '--max_download_restarts', type=int, default=50,
                        help="Def: 50. Max download restarts if throttling/low download speed detected." +
                             "Increase max download speed threshold in download_from_youtube_urls.py")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    MAX_DOWNLOAD_RESTARTS = args.max_download_restarts
    dw_args = ["python3", "download_from_youtube_urls.py",
               "--url_csv", args.url_csv,
               "--download_dir", args.download_dir]

    if args.force_res is not None:
        dw_args.append("--force_res")
        dw_args.append(args.force_res)

    i = 0
    return_status = None
    while return_status != 0:
        return_status = call(dw_args)
        if return_status == 2:
            print("Restarting download")
        i += 1
        if i > MAX_DOWNLOAD_RESTARTS:
            print(f"Aboirting. Max restarts exceeded {MAX_DOWNLOAD_RESTARTS}")
            print("Increase MAX_DOWNLOAD_RESTARTS for increased download restart tries")


if __name__ == "__main__":
    main()
