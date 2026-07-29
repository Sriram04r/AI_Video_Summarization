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

import re
def extract_video_id(url: str):
    regex = r"(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

@router.post("/youtube", status_code=status.HTTP_201_CREATED)
def process_youtube_link(
    req: YouTubeUploadRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video_yt_id = extract_video_id(req.url)
    if not video_yt_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL. Could not extract video ID."
        )
        
    video_title = f"YouTube Video ({video_yt_id})"
    try:
        import requests
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_yt_id}&format=json"
        resp = requests.get(oembed_url, timeout=3)
        if resp.status_code == 200:
            video_title = resp.json().get("title", video_title)
    except Exception:
        pass
        
    # Register video in the database using a special scheme for file_path
    new_video = Video(
        user_id=current_user.user_id,
        file_path=f"youtube://{video_yt_id}",
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
