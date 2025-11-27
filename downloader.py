import yt_dlp
import os
import asyncio

def _download(url, mode):
    # Create temp folder if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    
    ydl_opts = {
        # FIX 1: Use Video ID for filename instead of Title to avoid "File name too long"
        'outtmpl': 'temp/%(id)s.%(ext)s', 
        'format': 'bestvideo+bestaudio/best' if mode == "video" else 'bestaudio/best',
        'merge_output_format': 'mp4' if mode == "video" else None,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        # FIX 2: specific headers to make Facebook/TikTok think we are a real browser
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
        'postprocessors': [] if mode == "video" else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Prepare the expected filename
        filename = ydl.prepare_filename(info)
        
        # Ensure extension correction for audio
        if mode == "audio":
            base, _ = os.path.splitext(filename)
            filename = base + ".mp3"
            
    return os.path.abspath(filename)

async def download_video(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "video")

async def download_audio(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "audio")
