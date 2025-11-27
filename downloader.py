import yt_dlp
import os
import asyncio
import tempfile
import shutil
from moviepy.editor import VideoFileClip  # For compression

def compress_video_if_needed(input_path, max_size_mb=45):  # Leave headroom under 50MB
    file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    if file_size_mb <= max_size_mb:
        return input_path  # No need
    
    print(f"Compressing {file_size_mb:.1f}MB video...")
    output_path = input_path.replace('.mp4', '_compressed.mp4')
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, bitrate="1000k", preset="medium")  # ~10-20MB
    clip.close()
    os.remove(input_path)  # Clean original
    return output_path

def _download(url, mode):
    temp_dir = tempfile.mkdtemp(prefix="eveops_")
    outtmpl = os.path.join(temp_dir, '%(title).100s.%(ext)s')  # Short title
    
    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'best[filesize<45MB]/bestvideo[height<=720]+bestaudio/best[height<=720]',  # Prefer <45MB, 720p max
        'merge_output_format': 'mp4' if mode == "video" else None,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [] if mode == "video" else [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'extractor_retries': 3,
        'sleep_interval': 2,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == "audio" and not filename.endswith(".mp3"):
                filename = os.path.splitext(filename)[0] + ".mp3"
        
        # Compress video if needed
        if mode == "video" and os.path.exists(filename):
            filename = compress_video_if_needed(filename)
        
        if not os.path.exists(filename):
            raise Exception("No file downloaded")
        
        # Return absolute path
        return os.path.abspath(filename)
        
    except yt_dlp.utils.DownloadError as e:
        raise Exception(f"Download failed: {str(e).splitlines()[0]}")
    except Exception as e:
        raise Exception(f"Failed: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

async def download_video(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download, url, "video")

async def download_audio(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download, url, "audio")
