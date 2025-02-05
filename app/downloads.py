from yt_dlp import YoutubeDL
from os.path import join
from youtubesearchpython import VideosSearch


def find_youtube_link(search_query):
    """Find the first youtube link of the query"""
    
    video_search = VideosSearch(search_query, limit=1)
    
    return video_search.result()["result"][0]["link"]
    

def download_youtube_video(video_url, output_directory):
    """Download the video and save it to the output path"""
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Select the best quality video and audio available
        
        'quiet': True,  # Do not display messages in the console

        'outtmpl': join(output_directory, '%(title)s.%(ext)s'),  # Output file name
        
        'merge_output_format': 'mp4',  # Output format for merged audio and video
        'nocheckcertificate': True,  # Do not check SSL certificates
        'noplaylist': True,  # Ensure single video is downloaded, not a playlist
        
        
        'ffmpeg_location': '/usr/bin/ffmpeg'  # FFmpeg location on your computer   
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def download_youtube_audio(url, output_directory):
    """Download the audio and save it to the output path"""
    
    # Configuraciones para la descarga de audio
    ydl_opts = {
        'format': 'bestaudio/best',  # Selecciona la mejor calidad de audio disponible
        
        'quiet': True,  # No muestra mensajes en la consola
        
        'outtmpl': join(output_directory, '%(title)s.%(ext)s'),  # Nombre del archivo de salida
        
        'postprocessors': [{  # Usa FFmpeg para convertir el audio al formato deseado
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Aquí elegís el formato (mp3, wav, etc.)
            'preferredquality': '320',  # Calidad del audio (128, 192, 320 kbps)
        }],
        
        'ffmpeg_location': '/usr/bin/ffmpeg'  # Ubicación de FFmpeg en tu computadora   
    }

    # Descargar y procesar el audio
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
#######################################################################################################################

def download_tracks(tracks, audio=True):
    total_tracks = len(tracks)
        
    for index, track in enumerate(tracks):
        
        youtube_link = find_youtube_link(f"{track['track_name']} {track['artist']}")
        print(youtube_link)
        
        if audio:
            download_youtube_audio(youtube_link, 'downloads')
            print("Audio downloaded")
        else:
            download_youtube_video(youtube_link, 'downloads')

        progress = int((index + 1) / total_tracks * 100)
        
        

    

def get_playlist_songs(playlist_id, playlists_data):
    """Get the songs of a playlist given its id"""
    for playlist in playlists_data['items']:
        if playlist['id'] == playlist_id:
            return playlist['tracks']['items']
        
    return []
    
    
    
def download_song_with_progress(youtube_link, output_directory, audio=True):
    """Download a song and yield progress percentage."""
    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes', 1)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            progress = int((downloaded_bytes / total_bytes) * 100)
            yield progress

    ydl_opts = {
        'format': 'bestaudio/best' if audio else 'bestvideo+bestaudio/best',
        'quiet': True,
        'outtmpl': join(output_directory, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }] if audio else [],
        'ffmpeg_location': '.venv/bin/ffmpeg-git-20240629-amd64-static',
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_link])

    
    