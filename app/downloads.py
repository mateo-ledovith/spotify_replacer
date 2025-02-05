import os
from os.path import join
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

# Get FFmpeg path dynamically (allows overriding via environment variables)
FFMPEG_PATH = os.environ.get('FFMPEG_PATH', '/usr/bin/ffmpeg')


def find_youtube_link(search_query):
    """Finds the first YouTube link matching the search query."""
    video_search = VideosSearch(search_query, limit=1)
    return video_search.result()["result"][0]["link"]


def download_youtube_media(video_url, output_directory, audio_only=True):
    """
    Downloads a YouTube video or audio file.

    :param video_url: The YouTube link to download.
    :param output_directory: The folder where the file will be saved.
    :param audio_only: If True, downloads only audio; otherwise, downloads video.
    """
    ydl_opts = {
        'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
        'quiet': True,
        'outtmpl': join(output_directory, '%(title)s.%(ext)s'),
        'ffmpeg_location': FFMPEG_PATH,
        'noplaylist': True,  # Prevents downloading entire playlists
        'nocheckcertificate': True,  # Avoids SSL verification issues
    }

    if audio_only:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])