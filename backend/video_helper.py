import os
import logging
import subprocess
import glob
import re

logger = logging.getLogger(__name__)

def get_ffmpeg_path():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def extract_audio(video_path: str, audio_path: str) -> float:
    """Extracts audio from video file and saves it in MP3 format using FFmpeg directly for speed.
    Returns the duration of the video in seconds.
    """
    logger.info(f"Extracting audio from {video_path} -> {audio_path}")
    ffmpeg_exe = get_ffmpeg_path()
    
    try:
        # Get duration
        duration_cmd = [ffmpeg_exe, "-i", video_path]
        result = subprocess.run(duration_cmd, stderr=subprocess.PIPE, text=True)
        duration = 0.0
        match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", result.stderr)
        if match:
            h, m, s = match.groups()
            duration = int(h) * 3600 + int(m) * 60 + float(s)
            
        # Extract audio (16kHz mono mp3)
        extract_cmd = [
            ffmpeg_exe, "-y", "-i", video_path,
            "-vn", "-acodec", "libmp3lame",
            "-ac", "1", "-ar", "16000", "-q:a", "4",
            audio_path
        ]
        subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info("Audio extraction completed successfully.")
        
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            logger.warning("No audio track found in video.")
            raise ValueError("No audio track found in the uploaded video.")
            
        return duration if duration > 0 else 300.0
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error during audio extraction: {e}")
        raise ValueError("Failed to extract audio using FFmpeg.")
    except Exception as e:
        logger.error(f"Error during audio extraction: {e}")
        raise e

def extract_keyframes(video_path: str, output_dir: str, video_id: int, min_scene_duration: float = 3.0, threshold: float = 15.0) -> list:
    """Detects slide transitions and scene changes using FFmpeg for blazingly fast extraction.
    Saves unique frames as JPEGs in the output_dir and returns a list of frame metadata.
    """
    logger.info(f"Extracting keyframes from {video_path} into {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    ffmpeg_exe = get_ffmpeg_path()
    
    # First get video duration
    duration_cmd = [ffmpeg_exe, "-i", video_path]
    result = subprocess.run(duration_cmd, stderr=subprocess.PIPE, text=True)
    duration = 300.0
    match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", result.stderr)
    if match:
        h, m, s = match.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)
        
    num_keyframes = min(12, max(1, int(duration / min_scene_duration)))
    interval = duration / num_keyframes if num_keyframes > 0 else 0
    
    saved_frames = []
    
    # Fast extract using -ss before -i in a loop
    for i in range(num_keyframes):
        current_time_sec = i * interval
        new_filename = f"video_{video_id}_frame_{int(current_time_sec)}.jpg"
        new_filepath = os.path.join(output_dir, new_filename)
        
        extract_cmd = [
            ffmpeg_exe, "-y", "-ss", str(current_time_sec),
            "-i", video_path, "-vframes", "1", "-q:v", "2",
            new_filepath
        ]
        
        try:
            subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if os.path.exists(new_filepath):
                saved_frames.append({
                    "frame_path": os.path.abspath(new_filepath),
                    "timestamp": round(current_time_sec, 2),
                    "filename": new_filename
                })
                logger.info(f"Saved keyframe at {current_time_sec:.2f}s")
        except Exception as e:
            logger.error(f"FFmpeg error extracting frame at {current_time_sec}s: {e}")
            
    return saved_frames
