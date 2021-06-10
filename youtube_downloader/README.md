# Youtube Downloader

Using the Python library of [youtube-dl](https://github.com/ytdl-org/youtube-dl).

Install the pip version with `pip install youtube-dl`

## Usage

```bash
$ python download_from_youtube -u URL_SRC_CSV_PATH -v VIDEO_SAVE_DIR
```

The `URL_SRC_CSV_PATH` csv file msut have data in the format: `channel, format, lang, yt_title, yt_url`. Among these the `format` and `yt_url` are the most important ones.

Example url file is provided in `yt_urls.csv`
