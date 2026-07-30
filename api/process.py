import os
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from database.schema import Video, Summary, Frame, History
from backend.database_utils import get_db, SessionLocal
from api.auth import get_current_user, UserProfile
from backend.video_helper import extract_audio, extract_keyframes
from backend.ai_helper import (
    transcribe_audio_with_gemini, 
    transcribe_audio_with_groq,
    transcribe_audio_locally, 
    generate_summaries_and_notes, 
    generate_quiz_and_questions
)
from backend.pdf_helper import generate_pdf_report

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/video", tags=["Video Processing Pipeline"])

# Global memory-based progress store. Key: video_id, Value: dict of status, progress, message, error
processing_status = {}

def process_video_pipeline(video_id: int, language: str, difficulty: str, personalized_mode: str, use_cloud_stt: bool):
    """Orchestrated pipeline running in the background."""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.video_id == video_id).first()
        if not video:
            logger.error(f"Video {video_id} not found in background pipeline.")
            return

        is_youtube = video.file_path.startswith("youtube://")
        youtube_id = video.file_path.replace("youtube://", "") if is_youtube else None
        
        transcripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "transcripts")
        os.makedirs(transcripts_dir, exist_ok=True)
        transcript_file_path = os.path.join(transcripts_dir, f"video_{video_id}_transcript.txt")
        audio_path = os.path.join(transcripts_dir, f"video_{video_id}.mp3")
        
        if is_youtube:
            # Phase 1: Skip audio extraction
            processing_status[video_id] = {
                "status": "processing",
                "progress": 10,
                "message": "Fetching direct YouTube transcript...",
                "error": None
            }
            video.duration = 0
            db.commit()
            
            # Phase 2: Download subtitles
            processing_status[video_id] = {
                "status": "processing",
                "progress": 30,
                "message": "Downloading subtitles directly from YouTube...",
                "error": None
            }
            
            try:
                rapid_api_key = os.getenv("RAPID_API_KEY")
                rapid_api_host = os.getenv("RAPID_API_HOST")
                
                if rapid_api_key and rapid_api_host:
                    import requests
                    logger.info("Using RapidAPI to fetch transcript and bypass IP ban...")
                    
                    # Matches Solid API "Youtube Transcript" format
                    url = f"https://{rapid_api_host}/api/transcript-with-url"
                    youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
                    querystring = {"url": youtube_url, "flat_text": "true", "lang": "en"}
                    headers = {
                        "X-RapidAPI-Key": rapid_api_key,
                        "X-RapidAPI-Host": rapid_api_host
                    }
                    response = requests.get(url, headers=headers, params=querystring)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict):
                            if data.get('success') is False or 'error' in data:
                                error_msg = data.get('error', data.get('message', 'Unknown RapidAPI error'))
                                raise Exception(f"YouTube Transcript not available: {error_msg}")
                                
                            if 'transcript' in data:
                                transcript_text = str(data['transcript'])
                            elif 'data' in data:
                                transcript_text = str(data['data'])
                            elif 'text' in data:
                                transcript_text = str(data['text'])
                            else:
                                transcript_text = str(data)
                        else:
                            transcript_text = str(data)
                    else:
                        raise Exception(f"RapidAPI request failed: {response.status_code} - {response.text}")
                        
                else:
                    # Fallback to normal library (works locally, but banned on Render)
                    from youtube_transcript_api import YouTubeTranscriptApi
                    
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(youtube_id)
                    except AttributeError:
                        transcript_list = YouTubeTranscriptApi().list(youtube_id)
                    
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                    except Exception:
                        transcript = next(iter(transcript_list))
                        if transcript.language_code != 'en' and transcript.is_translatable:
                            transcript = transcript.translate('en')
                    
                    transcript_data = transcript.fetch()
                    transcript_text = " ".join([t['text'] for t in transcript_data])
            except Exception as e:
                # Catch YouTube IP Bans specifically for clearer error messages
                err_msg = str(e)
                if "429 Client Error: Too Many Requests" in err_msg or "YouTubeRequestFailed" in err_msg:
                    raise Exception("YouTube has blocked this server from downloading transcripts (Error 429). Please setup a RapidAPI key as instructed to bypass this block.")
                raise Exception(f"Failed to fetch YouTube transcript: {err_msg}")
            
            with open(transcript_file_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
                
            # Phase 3: Skip Keyframes
            processing_status[video_id] = {
                "status": "processing",
                "progress": 60,
                "message": "Skipping visual analysis for YouTube video...",
                "error": None
            }
        else:
            # Phase 1: Extract Audio (10%)
            processing_status[video_id] = {
                "status": "processing",
                "progress": 10,
                "message": "Extracting audio track from video...",
                "error": None
            }
            
            duration = extract_audio(video.file_path, audio_path)
            video.duration = duration
            db.commit()
            
            # Phase 2: Speech-to-Text Transcription (45%)
            processing_status[video_id] = {
                "status": "processing",
                "progress": 30,
                "message": "Converting speech to text (this may take a moment)...",
                "error": None
            }
            
            transcript_text = ""
            # Check if we should use Cloud STT or local Whisper
            if use_cloud_stt:
                provider = os.getenv("AI_PROVIDER", "gemini").lower()
                if provider == "groq" and os.getenv("GROQ_API_KEY"):
                    try:
                        transcript_text = transcribe_audio_with_groq(audio_path)
                    except Exception as ex:
                        logger.error(f"Groq transcription failed, falling back to local Whisper: {ex}")
                        transcript_text = transcribe_audio_locally(audio_path)
                elif provider == "gemini" and os.getenv("GEMINI_API_KEY"):
                    try:
                        transcript_text = transcribe_audio_with_gemini(audio_path)
                    except Exception as ex:
                        logger.error(f"Gemini transcription failed, falling back to local Whisper: {ex}")
                        transcript_text = transcribe_audio_locally(audio_path)
                else:
                    transcript_text = transcribe_audio_locally(audio_path)
            else:
                transcript_text = transcribe_audio_locally(audio_path)
                
            # Save transcript text file
            with open(transcript_file_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
                
            # Phase 3: CV Keyframe Extraction (60%)
            processing_status[video_id] = {
                "status": "processing",
                "progress": 60,
                "message": "Analyzing visual scene changes and slide transitions...",
                "error": None
            }
            
            frames_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frames", f"video_{video_id}")
            keyframes = extract_keyframes(video.file_path, frames_dir, video_id)
            
            # Save frames in database
            for kf in keyframes:
                db_frame = Frame(
                    video_id=video_id,
                    frame_path=kf["frame_path"],
                    timestamp=kf["timestamp"]
                )
                db.add(db_frame)
            db.commit()
        
        # Phase 4 & 5: AI Generation Tasks (75%)
        processing_status[video_id] = {
            "status": "processing",
            "progress": 75,
            "message": "Generating summaries, quizzes, and personalized study notes in parallel...",
            "error": None
        }
        
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_summaries = executor.submit(
                generate_summaries_and_notes,
                transcript=transcript_text,
                language=language,
                difficulty=difficulty,
                personalized_mode=personalized_mode
            )
            future_quiz = executor.submit(
                generate_quiz_and_questions,
                transcript=transcript_text,
                language=language
            )
            
            summary_results = future_summaries.result()
            quiz_json, interview_json = future_quiz.result()
        
        # Phase 6: PDF Report Compilation (95%)
        processing_status[video_id] = {
            "status": "processing",
            "progress": 95,
            "message": "Compiling PDF summaries and reports...",
            "error": None
        }
        
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        report_path = os.path.join(reports_dir, f"video_{video_id}_report.pdf")
        
        generate_pdf_report(
            video_title=video.title,
            summary_data=summary_results,
            quiz_data_str=quiz_json,
            output_path=report_path
        )
        
        # Phase 7: Store in Database and complete (100%)
        db_summary = Summary(
            video_id=video_id,
            short_summary=summary_results.get("short_summary"),
            detailed_summary=summary_results.get("detailed_summary"),
            topic_summary=summary_results.get("topic_summary"),
            notes_important=summary_results.get("notes_important"),
            notes_revision=summary_results.get("notes_revision"),
            notes_study=summary_results.get("notes_study"),
            keywords=summary_results.get("keywords"),
            quiz=quiz_json,
            interview_questions=interview_json,
            transcript=transcript_text
        )
        db.add(db_summary)
        
        # Log activity
        history_entry = History(
            user_id=video.user_id,
            activity=f"Successfully analyzed video: {video.title}"
        )
        db.add(history_entry)
        db.commit()
        
        # Cleanup WAV file on completion to save space
        if not is_youtube and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass
                
        processing_status[video_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Analysis successfully completed!",
            "error": None
        }
        logger.info(f"Background processing of video {video_id} completed successfully.")
        
    except Exception as e:
        logger.error(f"Error in background processing pipeline for video {video_id}: {e}", exc_info=True)
        processing_status[video_id] = {
            "status": "failed",
            "progress": 100,
            "message": "Processing failed.",
            "error": str(e)
        }
        
        # Log failure activity
        try:
            video = db.query(Video).filter(Video.video_id == video_id).first()
            if video:
                history_entry = History(
                    user_id=video.user_id,
                    activity=f"Failed to analyze video: {video.title} (Error: {str(e)})"
                )
                db.add(history_entry)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.post("/process/{video_id}")
def start_processing(
    video_id: int,
    background_tasks: BackgroundTasks,
    language: str = "English",
    difficulty: str = "Intermediate",
    personalized_mode: str = "Student mode",
    use_cloud_stt: bool = True,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Starts the video processing background pipeline."""
    video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == current_user.user_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")
        
    # Check if already processed
    existing_summary = db.query(Summary).filter(Summary.video_id == video_id).first()
    if existing_summary:
        return {"detail": "Video is already processed and summaries are available.", "status": "completed"}
        
    # Set status to initialized
    processing_status[video_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Queuing video for analytical processing...",
        "error": None
    }
    
    # Enqueue task
    background_tasks.add_task(
        process_video_pipeline,
        video_id=video_id,
        language=language,
        difficulty=difficulty,
        personalized_mode=personalized_mode,
        use_cloud_stt=use_cloud_stt
    )
    
    return {"detail": "Video analytical pipeline initiated in the background.", "status": "pending"}


@router.get("/status/{video_id}")
def get_status(
    video_id: int,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the current processing state of a video."""
    video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == current_user.user_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")
        
    # Check database first: if summary exists, return completed
    summary = db.query(Summary).filter(Summary.video_id == video_id).first()
    if summary:
        return {
            "status": "completed",
            "progress": 100,
            "message": "Analysis completed successfully!",
            "error": None
        }
        
    # Fallback to background process tracker
    status_info = processing_status.get(video_id)
    if not status_info:
        return {
            "status": "unknown",
            "progress": 0,
            "message": "No active processing session found for this video.",
            "error": None
        }
        
    return status_info


@router.get("/results/{video_id}")
def get_results(
    video_id: int,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch transcription, summaries, quizzes, and keyframes for a successfully processed video."""
    video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == current_user.user_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found or unauthorized")
        
    summary = db.query(Summary).filter(Summary.video_id == video_id).first()
    if not summary:
        raise HTTPException(status_code=400, detail="Video has not been processed yet. Start processing first.")
        
    # Fetch keyframes
    frames = db.query(Frame).filter(Frame.video_id == video_id).all()
    frame_list = []
    for frame in frames:
        # Get frame filename from path
        filename = os.path.basename(frame.frame_path)
        frame_list.append({
            "frame_id": frame.frame_id,
            "timestamp": frame.timestamp,
            "filename": filename
        })
        
    # Sort frames chronologically by timestamp
    frame_list.sort(key=lambda x: x["timestamp"])
    
    return {
        "video_id": video.video_id,
        "title": video.title,
        "duration": video.duration,
        "filename": video.file_path if video.file_path.startswith("youtube://") else os.path.basename(video.file_path),
        "short_summary": summary.short_summary,
        "detailed_summary": summary.detailed_summary,
        "topic_summary": summary.topic_summary,
        "notes_important": summary.notes_important,
        "notes_revision": summary.notes_revision,
        "notes_study": summary.notes_study,
        "keywords": summary.keywords,
        "quiz": summary.quiz,
        "interview_questions": summary.interview_questions,
        "transcript": summary.transcript,
        "keyframes": frame_list
    }
