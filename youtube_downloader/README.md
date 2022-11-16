# Youtube Downloader

Using the Python library of [youtube-dl](https://github.com/ytdl-org/youtube-dl).

Install the pip version with `pip install youtube-dl`

## Usage

### Download YT videos with predefined URLs

```shell
python download_from_youtube_urls.py -u URL_SRC_CSV_PATH -v VIDEO_SAVE_DIR -min_s 200 -max_r 50
```

Download with throttling detection based restarts. If speed drops below 200KiB/s (Can be changed with `min_s`), youtube-dl stops and restarts download for `max_r` tries.

The `URL_SRC_CSV_PATH` csv file must have data in the format: `channel, format, lang, yt_title, yt_url`. Among these the `format` and `yt_url` are the most important ones.

Example url file is provided in `urls/soccer_fullmatch.csv`

### Download YT videos using Youtube Search

```shell
python download_from_youtube_search.py -u URL_SRC_CSV_PATH -v VIDEO_SAVE_DIR
```

## OUTPUT TEMPLATE

The `-o` option allows users to indicate a template for the output file names.

**tl;dr:** [navigate me to examples](#output-template-examples).

The basic usage is not to set any template arguments when downloading a single file, like in `youtube-dl -o funny_video.flv "https://some/video"`. However, it may contain special sequences that will be replaced when downloading each video. The special sequences may be formatted according to [python string formatting operations](https://docs.python.org/2/library/stdtypes.html#string-formatting). For example, `%(NAME)s` or `%(NAME)05d`. To clarify, that is a percent symbol followed by a name in parentheses, followed by formatting operations. Allowed names along with sequence type are:

-   `id` (string): Video identifier
-   `title` (string): Video title
-   `url` (string): Video URL
-   `ext` (string): Video filename extension
-   `alt_title` (string): A secondary title of the video
-   `display_id` (string): An alternative identifier for the video
-   `uploader` (string): Full name of the video uploader
-   `license` (string): License name the video is licensed under
-   `creator` (string): The creator of the video
-   `release_date` (string): The date (YYYYMMDD) when the video was released
-   `timestamp` (numeric): UNIX timestamp of the moment the video became available
-   `upload_date` (string): Video upload date (YYYYMMDD)
-   `uploader_id` (string): Nickname or id of the video uploader
-   `channel` (string): Full name of the channel the video is uploaded on
-   `channel_id` (string): Id of the channel
-   `location` (string): Physical location where the video was filmed
-   `duration` (numeric): Length of the video in seconds
-   `view_count` (numeric): How many users have watched the video on the platform
-   `like_count` (numeric): Number of positive ratings of the video
-   `dislike_count` (numeric): Number of negative ratings of the video
-   `repost_count` (numeric): Number of reposts of the video
-   `average_rating` (numeric): Average rating give by users, the scale used depends on the webpage
-   `comment_count` (numeric): Number of comments on the video
-   `age_limit` (numeric): Age restriction for the video (years)
-   `is_live` (boolean): Whether this video is a live stream or a fixed-length video
-   `start_time` (numeric): Time in seconds where the reproduction should start, as specified in the URL
-   `end_time` (numeric): Time in seconds where the reproduction should end, as specified in the URL
-   `format` (string): A human-readable description of the format
-   `format_id` (string): Format code specified by `--format`
-   `format_note` (string): Additional info about the format
-   `width` (numeric): Width of the video
-   `height` (numeric): Height of the video
-   `resolution` (string): Textual description of width and height
-   `tbr` (numeric): Average bitrate of audio and video in KBit/s
-   `abr` (numeric): Average audio bitrate in KBit/s
-   `acodec` (string): Name of the audio codec in use
-   `asr` (numeric): Audio sampling rate in Hertz
-   `vbr` (numeric): Average video bitrate in KBit/s
-   `fps` (numeric): Frame rate
-   `vcodec` (string): Name of the video codec in use
-   `container` (string): Name of the container format
-   `filesize` (numeric): The number of bytes, if known in advance
-   `filesize_approx` (numeric): An estimate for the number of bytes
-   `protocol` (string): The protocol that will be used for the actual download
-   `extractor` (string): Name of the extractor
-   `extractor_key` (string): Key name of the extractor
-   `epoch` (numeric): Unix epoch when creating the file
-   `autonumber` (numeric): Number that will be increased with each download, starting at `--autonumber-start`
-   `playlist` (string): Name or id of the playlist that contains the video
-   `playlist_index` (numeric): Index of the video in the playlist padded with leading zeros according to the total length of the playlist
-   `playlist_id` (string): Playlist identifier
-   `playlist_title` (string): Playlist title
-   `playlist_uploader` (string): Full name of the playlist uploader
-   `playlist_uploader_id` (string): Nickname or id of the playlist uploader

Available for the video that belongs to some logical chapter or section:

-   `chapter` (string): Name or title of the chapter the video belongs to
-   `chapter_number` (numeric): Number of the chapter the video belongs to
-   `chapter_id` (string): Id of the chapter the video belongs to

Available for the video that is an episode of some series or programme:

-   `series` (string): Title of the series or programme the video episode belongs to
-   `season` (string): Title of the season the video episode belongs to
-   `season_number` (numeric): Number of the season the video episode belongs to
-   `season_id` (string): Id of the season the video episode belongs to
-   `episode` (string): Title of the video episode
-   `episode_number` (numeric): Number of the video episode within a season
-   `episode_id` (string): Id of the video episode

Available for the media that is a track or a part of a music album:

-   `track` (string): Title of the track
-   `track_number` (numeric): Number of the track within an album or a disc
-   `track_id` (string): Id of the track
-   `artist` (string): Artist(s) of the track
-   `genre` (string): Genre(s) of the track
-   `album` (string): Title of the album the track belongs to
-   `album_type` (string): Type of the album
-   `album_artist` (string): List of all artists appeared on the album
-   `disc_number` (numeric): Number of the disc or other physical medium the track belongs to
-   `release_year` (numeric): Year (YYYY) when the album was released

Each aforementioned sequence when referenced in an output template will be replaced by the actual value corresponding to the sequence name. Note that some of the sequences are not guaranteed to be present since they depend on the metadata obtained by a particular extractor. Such sequences will be replaced with placeholder value provided with `--output-na-placeholder` (`NA` by default).

For example for `-o %(title)s-%(id)s.%(ext)s` and an mp4 video with title `youtube-dl test video` and id `BaW_jenozKcj`, this will result in a `youtube-dl test video-BaW_jenozKcj.mp4` file created in the current directory.

For numeric sequences you can use numeric related formatting, for example, `%(view_count)05d` will result in a string with view count padded with zeros up to 5 characters, like in `00042`.

Output templates can also contain arbitrary hierarchical path, e.g. `-o '%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s'` which will result in downloading each video in a directory corresponding to this path template. Any missing directory will be automatically created for you.

To use percent literals in an output template use `%%`. To output to stdout use `-o -`.

The current default template is `%(title)s-%(id)s.%(ext)s`.

In some cases, you don't want special characters such as 中, spaces, or &, such as when transferring the downloaded filename to a Windows system or the filename through an 8bit-unsafe channel. In these cases, add the `--restrict-filenames` flag to get a shorter title:

#### Output template examples

Note that on Windows you may need to use double quotes instead of single.

```bash
youtube-dl --get-filename -o '%(title)s.%(ext)s' BaW_jenozKc
youtube-dl test video ''_ä↭𝕐.mp4    # All kinds of weird characters

youtube-dl --get-filename -o '%(title)s.%(ext)s' BaW_jenozKc --restrict-filenames
youtube-dl_test_video_.mp4          # A simple file name

# Download YouTube playlist videos in separate directory indexed by video order in a playlist
youtube-dl -o '%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s' https://www.youtube.com/playlist?list=PLwiyx1dc3P2JR9N8gQaQN_BCvlSlap7re

# Download all playlists of YouTube channel/user keeping each playlist in separate directory:
youtube-dl -o '%(uploader)s/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s' https://www.youtube.com/user/TheLinuxFoundation/playlists

# Download Udemy course keeping each chapter in separate directory under MyVideos directory in your home
youtube-dl -u user -p password -o '~/MyVideos/%(playlist)s/%(chapter_number)s - %(chapter)s/%(title)s.%(ext)s' https://www.udemy.com/java-tutorial/

# Download entire series season keeping each series and each season in separate directory under C:/MyVideos
youtube-dl -o "C:/MyVideos/%(series)s/%(season_number)s - %(season)s/%(episode_number)s - %(episode)s.%(ext)s" https://videomore.ru/kino_v_detalayah/5_sezon/367617

# Stream the video being downloaded to stdout
youtube-dl -o - BaW_jenozKc
```

## References

-   [YoutubeDL GitHub](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl)

-   [YoutubeDL Python Options Reference](https://github.com/ytdl-org/youtube-dl/blob/f19eae429a2c999db143060fded506dc52aaa398/youtube_dl/options.py#L144)

## Format code reference

```
'5': {'ext': 'flv', 'width': 400, 'height': 240, 'acodec': 'mp3', 'abr': 64, 'vcodec': 'h263'},
'6': {'ext': 'flv', 'width': 450, 'height': 270, 'acodec': 'mp3', 'abr': 64, 'vcodec': 'h263'},
'13': {'ext': '3gp', 'acodec': 'aac', 'vcodec': 'mp4v'},
'17': {'ext': '3gp', 'width': 176, 'height': 144, 'acodec': 'aac', 'abr': 24, 'vcodec': 'mp4v'},
'18': {'ext': 'mp4', 'width': 640, 'height': 360, 'acodec': 'aac', 'abr': 96, 'vcodec': 'h264'},
'22': {'ext': 'mp4', 'width': 1280, 'height': 720, 'acodec': 'aac', 'abr': 192, 'vcodec': 'h264'},
'34': {'ext': 'flv', 'width': 640, 'height': 360, 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264'},
'35': {'ext': 'flv', 'width': 854, 'height': 480, 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264'},

# itag 36 videos are either 320x180 (BaW_jenozKc) or 320x240 (__2ABJjxzNo), abr varies as well
'36': {'ext': '3gp', 'width': 320, 'acodec': 'aac', 'vcodec': 'mp4v'},
'37': {'ext': 'mp4', 'width': 1920, 'height': 1080, 'acodec': 'aac', 'abr': 192, 'vcodec': 'h264'},
'38': {'ext': 'mp4', 'width': 4096, 'height': 3072, 'acodec': 'aac', 'abr': 192, 'vcodec': 'h264'},
'43': {'ext': 'webm', 'width': 640, 'height': 360, 'acodec': 'vorbis', 'abr': 128, 'vcodec': 'vp8'},
'44': {'ext': 'webm', 'width': 854, 'height': 480, 'acodec': 'vorbis', 'abr': 128, 'vcodec': 'vp8'},
'45': {'ext': 'webm', 'width': 1280, 'height': 720, 'acodec': 'vorbis', 'abr': 192, 'vcodec': 'vp8'},
'46': {'ext': 'webm', 'width': 1920, 'height': 1080, 'acodec': 'vorbis', 'abr': 192, 'vcodec': 'vp8'},
'59': {'ext': 'mp4', 'width': 854, 'height': 480, 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264'},
'78': {'ext': 'mp4', 'width': 854, 'height': 480, 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264'},

# 3D videos
'82': {'ext': 'mp4', 'height': 360, 'format_note': '3D', 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264', 'preference': -20},
'83': {'ext': 'mp4', 'height': 480, 'format_note': '3D', 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264', 'preference': -20},
'84': {'ext': 'mp4', 'height': 720, 'format_note': '3D', 'acodec': 'aac', 'abr': 192, 'vcodec': 'h264', 'preference': -20},
'85': {'ext': 'mp4', 'height': 1080, 'format_note': '3D', 'acodec': 'aac', 'abr': 192, 'vcodec': 'h264', 'preference': -20},
'100': {'ext': 'webm', 'height': 360, 'format_note': '3D', 'acodec': 'vorbis', 'abr': 128, 'vcodec': 'vp8', 'preference': -20},
'101': {'ext': 'webm', 'height': 480, 'format_note': '3D', 'acodec': 'vorbis', 'abr': 192, 'vcodec': 'vp8', 'preference': -20},
'102': {'ext': 'webm', 'height': 720, 'format_note': '3D', 'acodec': 'vorbis', 'abr': 192, 'vcodec': 'vp8', 'preference': -20},

# Apple HTTP Live Streaming
'91': {'ext': 'mp4', 'height': 144, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 48, 'vcodec': 'h264', 'preference': -10},
'92': {'ext': 'mp4', 'height': 240, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 48, 'vcodec': 'h264', 'preference': -10},
'93': {'ext': 'mp4', 'height': 360, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264', 'preference': -10},
'94': {'ext': 'mp4', 'height': 480, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 128, 'vcodec': 'h264', 'preference': -10},
'95': {'ext': 'mp4', 'height': 720, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 256, 'vcodec': 'h264', 'preference': -10},
'96': {'ext': 'mp4', 'height': 1080, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 256, 'vcodec': 'h264', 'preference': -10},
'132': {'ext': 'mp4', 'height': 240, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 48, 'vcodec': 'h264', 'preference': -10},
'151': {'ext': 'mp4', 'height': 72, 'format_note': 'HLS', 'acodec': 'aac', 'abr': 24, 'vcodec': 'h264', 'preference': -10},

# DASH mp4 video
'133': {'ext': 'mp4', 'height': 240, 'format_note': 'DASH video', 'vcodec': 'h264'},
'134': {'ext': 'mp4', 'height': 360, 'format_note': 'DASH video', 'vcodec': 'h264'},
'135': {'ext': 'mp4', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'h264'},
'136': {'ext': 'mp4', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'h264'},
'137': {'ext': 'mp4', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'h264'},
'138': {'ext': 'mp4', 'format_note': 'DASH video', 'vcodec': 'h264'},  # Height can vary (https://github.com/ytdl-org/youtube-dl/issues/4559)
'160': {'ext': 'mp4', 'height': 144, 'format_note': 'DASH video', 'vcodec': 'h264'},
'212': {'ext': 'mp4', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'h264'},
'264': {'ext': 'mp4', 'height': 1440, 'format_note': 'DASH video', 'vcodec': 'h264'},
'298': {'ext': 'mp4', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'h264', 'fps': 60},
'299': {'ext': 'mp4', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'h264', 'fps': 60},
'266': {'ext': 'mp4', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'h264'},

# Dash mp4 audio
'139': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'abr': 48, 'container': 'm4a_dash'},
'140': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'abr': 128, 'container': 'm4a_dash'},
'141': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'abr': 256, 'container': 'm4a_dash'},
'256': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'container': 'm4a_dash'},
'258': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'aac', 'container': 'm4a_dash'},
'325': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'dtse', 'container': 'm4a_dash'},
'328': {'ext': 'm4a', 'format_note': 'DASH audio', 'acodec': 'ec-3', 'container': 'm4a_dash'},

# Dash webm
'167': {'ext': 'webm', 'height': 360, 'width': 640, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
'168': {'ext': 'webm', 'height': 480, 'width': 854, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
'169': {'ext': 'webm', 'height': 720, 'width': 1280, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
'170': {'ext': 'webm', 'height': 1080, 'width': 1920, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
'218': {'ext': 'webm', 'height': 480, 'width': 854, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
'219': {'ext': 'webm', 'height': 480, 'width': 854, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp8'},
'278': {'ext': 'webm', 'height': 144, 'format_note': 'DASH video', 'container': 'webm', 'vcodec': 'vp9'},
'242': {'ext': 'webm', 'height': 240, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'243': {'ext': 'webm', 'height': 360, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'244': {'ext': 'webm', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'245': {'ext': 'webm', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'246': {'ext': 'webm', 'height': 480, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'247': {'ext': 'webm', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'248': {'ext': 'webm', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'271': {'ext': 'webm', 'height': 1440, 'format_note': 'DASH video', 'vcodec': 'vp9'},
# itag 272 videos are either 3840x2160 (e.g. RtoitU2A-3E) or 7680x4320 (sLprVF6d7Ug)
'272': {'ext': 'webm', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'302': {'ext': 'webm', 'height': 720, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},
'303': {'ext': 'webm', 'height': 1080, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},
'308': {'ext': 'webm', 'height': 1440, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},
'313': {'ext': 'webm', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'vp9'},
'315': {'ext': 'webm', 'height': 2160, 'format_note': 'DASH video', 'vcodec': 'vp9', 'fps': 60},

# Dash webm audio
'171': {'ext': 'webm', 'acodec': 'vorbis', 'format_note': 'DASH audio', 'abr': 128},
'172': {'ext': 'webm', 'acodec': 'vorbis', 'format_note': 'DASH audio', 'abr': 256},

# Dash webm audio with opus inside
'249': {'ext': 'webm', 'format_note': 'DASH audio', 'acodec': 'opus', 'abr': 50},
'250': {'ext': 'webm', 'format_note': 'DASH audio', 'acodec': 'opus', 'abr': 70},
'251': {'ext': 'webm', 'format_note': 'DASH audio', 'acodec': 'opus', 'abr': 160},

# RTMP (unnamed)
'_rtmp': {'protocol': 'rtmp'},

# av01 video only formats sometimes served with "unknown" codecs
'394': {'acodec': 'none', 'vcodec': 'av01.0.05M.08'},
'395': {'acodec': 'none', 'vcodec': 'av01.0.05M.08'},
'396': {'acodec': 'none', 'vcodec': 'av01.0.05M.08'},
'397': {'acodec': 'none', 'vcodec': 'av01.0.05M.08'},
```
