import yt_dlp
import os
import asyncio
import re
import uuid

def _download(url, mode):
    os.makedirs("temp", exist_ok=True)
    
    # Generate a unique short filename
    file_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID
    if mode == "video":
        outtmpl = f'temp/{file_id}.%(ext)s'
    else:
        outtmpl = f'temp/{file_id}.%(ext)s'
    
    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'bestvideo+bestaudio/best' if mode == "video" else 'bestaudio/best',
        'merge_output_format': 'mp4' if mode == "video" else None,
        'noplaylist': True,
        'quiet': False,  # Set to False for debugging
        'no_warnings': False,
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
            # First extract info without downloading
            info = ydl.extract_info(url, download=False)
            
            if '_type' in info and info['_type'] == 'playlist':
                info = info['entries'][0]
            
            # Now download with our simple filename
            ydl.download([url])
            
            # Find the actual downloaded file
            expected_ext = 'mp4' if mode == "video" else 'mp3'
            expected_filename = f"temp/{file_id}.{expected_ext}"
            
            # Check if file exists with expected name
            if os.path.exists(expected_filename):
                return os.path.abspath(expected_filename)
            
            # If not, look for any file with our UUID
            for file in os.listdir("temp"):
                if file.startswith(file_id):
                    file_path = os.path.abspath(f"temp/{file}")
                    
                    # If we need mp3 but file is mp4, convert it
                    if mode == "audio" and file.endswith('.mp4'):
                        import subprocess
                        mp3_path = file_path.rsplit('.', 1)[0] + '.mp3'
                        subprocess.run([
                            'ffmpeg', '-i', file_path, 
                            '-codec:a', 'libmp3lame', 
                            '-q:a', '2', 
                            mp3_path,
                            '-y'
                        ], capture_output=True)
                        os.remove(file_path)
                        return mp3_path
                    
                    return file_path
            
            return None
            
    except Exception as e:
        print(f"Download error: {str(e)}")
        # Clean up any partial files
        try:
            for file in os.listdir("temp"):
                if file.startswith(file_id):
                    os.remove(f"temp/{file}")
        except:
            pass
        return None

async def download_video(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "video")

async def download_audio(url):
    return await asyncio.get_event_loop().run_in_executor(None, _download, url, "audio")
