from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database.schema import History, Video, Summary
from backend.database_utils import get_db
from api.auth import get_current_user, UserProfile
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/history", tags=["History & User Activities"])

class HistoryResponse(BaseModel):
    history_id: int
    activity: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class VideoItemResponse(BaseModel):
    video_id: int
    title: str
    upload_date: datetime
    has_analysis: bool
    duration: Optional[float] = None

    class Config:
        from_attributes = True

@router.get("", response_model=List[HistoryResponse])
def get_user_history(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all activities performed by the current logged-in user."""
    activities = db.query(History).filter(History.user_id == current_user.user_id).order_by(History.timestamp.desc()).all()
    return activities

@router.get("/videos", response_model=List[VideoItemResponse])
def get_user_videos(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all videos uploaded by the user, indicating if summaries are available."""
    videos = db.query(Video).filter(Video.user_id == current_user.user_id).order_by(Video.upload_date.desc()).all()
    
    result = []
    for video in videos:
        # Check if a summary exists for this video
        summary_exists = db.query(Summary).filter(Summary.video_id == video.video_id).first() is not None
        result.append(VideoItemResponse(
            video_id=video.video_id,
            title=video.title,
            upload_date=video.upload_date,
            has_analysis=summary_exists,
            duration=video.duration
        ))
    return result

@router.delete("/video/{video_id}", status_code=status.HTTP_200_OK)
def delete_video(
    video_id: int,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a video and all associated processing data (summaries, frames, database records)."""
    video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == current_user.user_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")
    
    # Clean up physical files
    if os.path.exists(video.file_path):
        try:
            os.remove(video.file_path)
        except Exception:
            pass
            
    # Clean up associated frames files from disk
    frames = db.query(Frame).filter(Frame.video_id == video_id).all()
    for frame in frames:
        if os.path.exists(frame.frame_path):
            try:
                os.remove(frame.frame_path)
            except Exception:
                pass
                
    # Delete database records (Cascading triggers or SQLAlchemy cascade will handle child tables if foreign keys have CASCADE)
    db.delete(video)
    
    # Log deletion
    history_entry = History(
        user_id=current_user.user_id,
        activity=f"Deleted video: {video.title}"
    )
    db.add(history_entry)
    db.commit()
    
    return {"detail": "Video and all associated analytical data deleted successfully"}

import os
from database.schema import Frame

@router.delete("/clear", status_code=status.HTTP_200_OK)
def clear_all_history(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all videos and associated data for the current user."""
    videos = db.query(Video).filter(Video.user_id == current_user.user_id).all()
    
    for video in videos:
        # Clean up physical files
        if os.path.exists(video.file_path):
            try:
                os.remove(video.file_path)
            except Exception:
                pass
                
        # Clean up associated frames files from disk
        frames = db.query(Frame).filter(Frame.video_id == video.video_id).all()
        for frame in frames:
            if os.path.exists(frame.frame_path):
                try:
                    os.remove(frame.frame_path)
                except Exception:
                    pass
        
        db.delete(video)
        
    # Log deletion
    history_entry = History(
        user_id=current_user.user_id,
        activity="Cleared all video history"
    )
    db.add(history_entry)
    db.commit()
    
    return {"detail": "All history cleared successfully"}
