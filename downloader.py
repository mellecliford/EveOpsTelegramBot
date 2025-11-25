import yt_dlp
import os
import asyncio

def _download(url, mode):
    os.makedirs("temp", exist_ok=True)
    
    ydl_opts = {
        'outtmpl': 'temp/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best' if mode == "video" else 'bestaudio/best',
        'merge_output_format': 'mp4' if mode == "video" else None,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [] if mode == "video" else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == "audio" and not filename.endswith(".mp3"):
            filename = os.path.splitext(filename)[0] + ".mp3"
    return os.path.abspath(filename)

async def download_video(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "video")

async def download_audio(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "audio")