#!/bin/bash
python download_from_youtube_urls.py -u urls/ufc_fullmatch.csv -v ../datasets/ufc/orig_video
python download_from_youtube_urls.py -u urls/soccer_fullmatch.csv -v ../datasets/soccer/orig_video
python download_from_youtube_urls.py -u urls/boxing_fullmatch.csv -v ../datasets/boxing/orig_video
python download_from_youtube_urls.py -u urls/tennis_fullmatch.csv -v ../datasets/tennis/orig_video
python download_from_youtube_urls.py -u urls/basketball_fullmatch.csv -v ../datasets/basketball/orig_video
