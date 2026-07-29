import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.schema import Video, Summary, User
from backend.database_utils import get_db
from backend.security import decode_access_token

router = APIRouter(prefix="/video", tags=["Reports & Exports"])

@router.get("/report/{video_id}")
def download_report(
    video_id: int,
    token: str = "",
    db: Session = Depends(get_db)
):
    """Retrieve and download the compiled PDF report for a processed video."""
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")
        
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
        
    current_user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    # Verify video ownership
    video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == current_user.user_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")
        
    # Check if analysis has run
    summary = db.query(Summary).filter(Summary.video_id == video_id).first()
    if not summary:
        raise HTTPException(status_code=400, detail="Video has not been processed yet. Report is unavailable.")
        
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    pdf_path = os.path.join(reports_dir, f"video_{video_id}_report.pdf")
    
    if not os.path.exists(pdf_path):
        # Fallback: Regenerate PDF if summary data exists but file is missing
        try:
            from backend.pdf_helper import generate_pdf_report
            import json
            summary_dict = {
                "short_summary": summary.short_summary,
                "detailed_summary": summary.detailed_summary,
                "topic_summary": summary.topic_summary,
                "notes_important": summary.notes_important,
                "notes_revision": summary.notes_revision,
                "notes_study": summary.notes_study,
                "keywords": summary.keywords
            }
            generate_pdf_report(
                video_title=video.title,
                summary_data=summary_dict,
                quiz_data_str=summary.quiz,
                output_path=pdf_path
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate report file: {str(e)}")
            
    # Format a clean browser download name
    safe_title = "".join([c if c.isalnum() or c in (" ", "-", "_") else "_" for c in video.title])
    safe_title = safe_title.replace(" ", "_")
    download_name = f"{safe_title}_Report.pdf"
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=download_name
    )
