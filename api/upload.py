import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import yt_dlp
from database.schema import Video, History
from backend.database_utils import get_db
from api.auth import get_current_user, UserProfile

router = APIRouter(prefix="/video", tags=["Video Upload"])


ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file extension
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Save the file temporarily to check size
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4()}{ext}"
    target_path = os.path.join(uploads_dir, unique_filename)
    
    try:
        size = 0
        with open(target_path, "wb") as buffer:
            while chunk := await file.read(8192):
                buffer.write(chunk)
    except HTTPException as he:
        raise he
    except Exception as e:
        if os.path.exists(target_path):
            os.remove(target_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to disk: {str(e)}"
        )
        
    # Register video in the database
    new_video = Video(
        user_id=current_user.user_id,
        file_path=os.path.abspath(target_path),
        title=file.filename,
        duration=None  # Will be extracted during audio processing
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    
    # Log activity
    history_entry = History(
        user_id=current_user.user_id,
        activity=f"Uploaded video: {file.filename} (ID: {new_video.video_id})"
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "video_id": new_video.video_id,
        "title": new_video.title,
        "file_path": new_video.file_path,
        "upload_date": new_video.upload_date
    }

class YouTubeUploadRequest(BaseModel):
    url: str

@router.post("/youtube", status_code=status.HTTP_201_CREATED)
def process_youtube_link(
    req: YouTubeUploadRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4()}.mp4"
    target_path = os.path.join(uploads_dir, unique_filename)
    
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_path = 'ffmpeg'

    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        'outtmpl': target_path,
        'quiet': True,
        'noplaylist': True,
        'ffmpeg_location': ffmpeg_path,
        'extractor_args': {'youtube': ['player_client=ios,android']}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
            title = info.get('title') if info else None
            if not title:
                title = 'YouTube Video'
            video_title = f"{title}.mp4"
            
            # No file size check needed
    except HTTPException as he:
        raise he
    except yt_dlp.utils.DownloadError as e:
        if os.path.exists(target_path):
            os.remove(target_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to download YouTube video: {str(e)}"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
        
    # Register video in the database
    new_video = Video(
        user_id=current_user.user_id,
        file_path=os.path.abspath(target_path),
        title=video_title,
        duration=None
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    
    # Log activity
    history_entry = History(
        user_id=current_user.user_id,
        activity=f"Imported YouTube video: {video_title} (ID: {new_video.video_id})"
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "video_id": new_video.video_id,
        "title": new_video.title,
        "file_path": new_video.file_path,
        "upload_date": new_video.upload_date
    }
