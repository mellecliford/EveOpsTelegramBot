import yt_dlp
import os
import asyncio
import re

def sanitize_filename(filename):
    """Sanitize filename to avoid filesystem issues"""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Limit filename length (max 100 characters)
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    return filename

def _download(url, mode):
    os.makedirs("temp", exist_ok=True)
    
    ydl_opts = {
        'outtmpl': 'temp/%(id)s.%(ext)s',  # Use video ID instead of title to avoid long filenames
        'format': 'bestvideo+bestaudio/best' if mode == "video" else 'bestaudio/best',
        'merge_output_format': 'mp4' if mode == "video" else None,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        
        # Better compatibility for social media platforms
        'extractor_args': {
            'facebook': {'format': 'best'},
            'tiktok': {'format': 'best'},
            'instagram': {'format': 'best'}
        },
        
        # HTTP headers to avoid blocking
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Connection': 'keep-alive',
        },
        
        'postprocessors': [] if mode == "video" else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Get the actual downloaded file
            if '_type' in info and info['_type'] == 'playlist':
                info = info['entries'][0]
            
            # Use original filename from yt-dlp
            original_filename = ydl.prepare_filename(info)
            
            if mode == "audio":
                # For audio, change extension to mp3
                base_name = os.path.splitext(original_filename)[0]
                final_filename = base_name + ".mp3"
                
                # Check if the mp3 file was created by FFmpeg
                if not os.path.exists(final_filename):
                    # If not, use the original file
                    final_filename = original_filename
            else:
                final_filename = original_filename
            
            return os.path.abspath(final_filename)
            
    except Exception as e:
        print(f"Download error: {e}")
        return None

async def download_video(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "video")

async def download_audio(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "audio")
