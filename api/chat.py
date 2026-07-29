from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database.schema import Summary
from backend.database_utils import get_db
from api.auth import get_current_user, UserProfile
from backend.ai_helper import chat_with_transcript

router = APIRouter(prefix="/video", tags=["Video Chat (RAG)"])

class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat/{video_id}", response_model=ChatResponse)
def chat_with_video(
    video_id: int,
    req: ChatRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about the video transcript context using Generative AI (RAG)."""
    # Fetch summary to get the transcript
    summary = db.query(Summary).filter(Summary.video_id == video_id).first()
    if not summary or not summary.transcript:
        raise HTTPException(
            status_code=400, 
            detail="Transcript is not available. Please ensure the video has been fully analyzed."
        )
        
    # Format history for generative AI SDK
    formatted_history = []
    if req.history:
        for msg in req.history:
            formatted_history.append({
                "role": msg.role,
                "content": msg.content
            })
            
    answer = chat_with_transcript(
        transcript=summary.transcript,
        question=req.question,
        chat_history=formatted_history
    )
    
    return ChatResponse(answer=answer)
