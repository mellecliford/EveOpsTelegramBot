import yt_dlp
import os
import asyncio
import tempfile

def _download(url, mode):
    temp_dir = tempfile.mkdtemp(prefix="eveops_")
    
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title).100s.%(ext)s'),  # ← FIXED: Shorten title to 100 chars
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
        # FB/TikTok fixes
        'extractor_retries': 3,
        'sleep_interval': 2,  # Rate limit
        'cookies': 'cookies.txt',  # For FB (create this file below)
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == "audio" and not filename.endswith(".mp3"):
                filename = os.path.splitext(filename)[0] + ".mp3"
        
        # Find the actual downloaded file (in case of merging)
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f.endswith(('.mp4', '.mp3')):
                    full_path = os.path.join(root, f)
                    return full_path
        
        raise Exception("No file downloaded")
        
    except yt_dlp.utils.DownloadError as e:
        raise Exception(f"Download failed: {str(e).splitlines()[0]}")  # Clean error
    except Exception as e:
        raise Exception(f"Failed: {str(e)}")
    finally:
        # Clean temp dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

async def download_video(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download, url, "video")

async def download_audio(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download, url, "audio")
