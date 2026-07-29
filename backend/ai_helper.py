import os
import json
import logging
from typing import Dict, Any, Tuple
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Ensure ffmpeg.exe exists in imageio_ffmpeg binaries folder and is added to system PATH
try:
    import shutil
    import imageio_ffmpeg
    bundled_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    bin_dir = os.path.dirname(bundled_ffmpeg)
    target_ffmpeg = os.path.join(bin_dir, "ffmpeg.exe")
    if not os.path.exists(target_ffmpeg):
        logger.info(f"Copying {bundled_ffmpeg} to {target_ffmpeg} for whisper subprocess support...")
        shutil.copy2(bundled_ffmpeg, target_ffmpeg)
    if bin_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + bin_dir
        logger.info(f"Added ffmpeg directory {bin_dir} to system PATH.")
except Exception as e:
    logger.warning(f"Failed to configure ffmpeg path helper: {e}")


def get_gemini_model():
    """Configure and return the Gemini model if API key is present."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set. AI features will fail or fall back.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

def get_groq_client():
    """Return configured Groq API client if key is present."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY is not set. AI features using Groq will fail.")
        return None
    from groq import Groq
    return Groq(api_key=api_key)

def transcribe_audio_with_gemini(audio_path: str) -> str:
    """Uploads audio file directly to Gemini API for high-speed cloud transcription."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required for Gemini cloud transcription.")
    
    genai.configure(api_key=api_key)
    logger.info(f"Uploading audio file {audio_path} to Gemini...")
    audio_file = genai.upload_file(path=audio_path)
    logger.info(f"Audio file uploaded. Requesting transcription from Gemini...")
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "Transcribe this audio file completely. Keep all spoken text verbatim. "
        "Do not summarize or edit. If there are multiple speakers, label them if possible. "
        "Provide clear transcription paragraphs."
    )
    
    response = model.generate_content([audio_file, prompt])
    
    # Clean up the file on Gemini cloud
    try:
        genai.delete_file(audio_file.name)
    except Exception as e:
        logger.error(f"Error deleting temporary file from Gemini: {e}")
        
    return response.text

def transcribe_audio_with_groq(audio_path: str) -> str:
    """Uploads audio file to Groq API for ultra-fast cloud transcription."""
    client = get_groq_client()
    if not client:
        raise ValueError("GROQ_API_KEY is required for Groq cloud transcription.")
    
    import time
    import subprocess
    import glob
    
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    chunks = [audio_path]
    chunk_dir = None
    
    if file_size_mb > 24:
        logger.info(f"Audio file size ({file_size_mb:.2f}MB) exceeds 24MB Groq limit. Chunking audio...")
        chunk_dir = audio_path + "_chunks"
        os.makedirs(chunk_dir, exist_ok=True)
        chunk_pattern = os.path.join(chunk_dir, "chunk_%03d.mp3")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-f", "segment", "-segment_time", "1800",
            "-c", "copy", chunk_pattern
        ]
        try:
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            chunks = sorted(glob.glob(os.path.join(chunk_dir, "chunk_*.mp3")))
            logger.info(f"Split audio into {len(chunks)} chunks.")
        except Exception as e:
            logger.error(f"Failed to chunk audio: {e}")
            raise e

    full_transcript = []
    
    for idx, chunk_path in enumerate(chunks):
        logger.info(f"Uploading chunk {idx+1}/{len(chunks)} to Groq...")
        last_error = None
        success = False
        for attempt in range(3):
            try:
                with open(chunk_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                      file=(os.path.basename(chunk_path), file.read()),
                      model="whisper-large-v3-turbo",
                      prompt="Transcribe this audio file completely. Keep all spoken text verbatim. Do not summarize or edit."
                    )
                    full_transcript.append(transcription.text)
                    success = True
                    break
            except Exception as e:
                last_error = e
                logger.warning(f"Groq transcription failed (attempt {attempt+1}/3): {e}")
                time.sleep(2)
                
        if not success:
            logger.error(f"Error during Groq transcription after 3 attempts: {last_error}")
            raise last_error
            
    if chunk_dir and os.path.exists(chunk_dir):
        for f in chunks:
            try:
                os.remove(f)
            except:
                pass
        try:
            os.rmdir(chunk_dir)
        except:
            pass

    return " ".join(full_transcript)

def transcribe_audio_locally(audio_path: str) -> str:
    """Uses local Whisper model to transcribe the audio file."""
    logger.info("Loading local Whisper model...")
    import whisper
    # Load 'base' model to balance accuracy and CPU speed (small was too slow for fallback)
    model = whisper.load_model("base")
    logger.info("Transcribing audio file locally...")
    result = model.transcribe(audio_path)
    return result.get("text", "")



def _generate_missing_key_dict(provider_name: str) -> Dict[str, str]:
    return {
        "short_summary": f"{provider_name} API key missing. Could not generate summary.",
        "detailed_summary": f"{provider_name} API key missing.",
        "topic_summary": f"{provider_name} API key missing.",
        "notes_important": f"{provider_name} API key missing.",
        "notes_revision": f"{provider_name} API key missing.",
        "notes_study": f"{provider_name} API key missing.",
        "keywords": "Error"
    }

def _generate_error_dict(e: Exception) -> Dict[str, str]:
    return {
        "short_summary": f"Failed to generate summary: {str(e)}",
        "detailed_summary": "Error during generation.",
        "topic_summary": "Error during generation.",
        "notes_important": "Error during generation.",
        "notes_revision": "Error during generation.",
        "notes_study": "Error during generation.",
        "keywords": "Error"
    }

def _sanitize_json_output(data: Dict[str, Any]) -> Dict[str, str]:
    """Ensures all values in the dictionary are strings to prevent database binding errors."""
    sanitized = {}
    for k, v in data.items():
        if isinstance(v, list):
            sanitized[k] = '\n'.join([str(item) for item in v])
        elif isinstance(v, dict):
            sanitized[k] = json.dumps(v, indent=2)
        else:
            sanitized[k] = str(v)
    return sanitized

def generate_summaries_and_notes(
    transcript: str, 
    language: str = "English", 
    difficulty: str = "Intermediate",
    personalized_mode: str = "Student mode"
) -> Dict[str, str]:
    """Generates short, detailed, and topic-wise summaries, plus notes tailored to preferences."""
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    prompt = f"""
    You are an expert AI educator and copywriter.
    Analyze the following video transcript and generate the requested summaries and learning notes.
    
    Target Language: {language}
    Target Difficulty Level: {difficulty} (Adjust explanation complexity and depth accordingly)
    Personalization Mode: {personalized_mode} (Tailor the emphasis and style of study notes for this mode)
    
    TRANSCRIPT:
    \"\"\"{transcript}\"\"\"
    
    You must output a JSON object containing exactly these fields. Do not add markdown wrappers around the JSON, return ONLY the raw JSON string:
    {{
        "short_summary": "A concise, single-paragraph summary (approx 100 words) summarizing the core message.",
        "detailed_summary": "A comprehensive, multi-paragraph summary covering all key aspects, arguments, and takeaways.",
        "topic_summary": "A structured, topic-by-topic summary showing what was covered and when/how, using bullet points.",
        "notes_important": "Key takeaways, crucial formulas/definitions, and main points that are absolute must-knows.",
        "notes_revision": "Ultra-short, highly scannable summary/cheatsheet notes for quick revision right before an exam or interview.",
        "notes_study": "In-depth study notes with explanations, structured hierarchies, and illustrative examples based on the transcript details.",
        "keywords": "A comma-separated string of the top 10 most relevant keywords, concepts, or topics covered (e.g. 'Machine Learning, Neural Networks, Backpropagation')."
    }}
    """

    if provider == "groq":
        client = get_groq_client()
        if not client:
            return _generate_missing_key_dict("Groq")
        try:
            logger.info("Requesting summaries from Groq...")
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful educational assistant that always returns raw JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            data = json.loads(chat_completion.choices[0].message.content)
            return _sanitize_json_output(data)
        except Exception as e:
            logger.error(f"Error generating summaries from Groq: {e}", exc_info=True)
            return _generate_error_dict(e)
            
    # Default: Gemini
    model = get_gemini_model()
    if not model:
        return _generate_missing_key_dict("Gemini")
        
    try:
        logger.info("Requesting summaries from Gemini...")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        return _sanitize_json_output(data)
    except Exception as e:
        logger.error(f"Error generating summaries from Gemini: {e}")
        return _generate_error_dict(e)

def generate_quiz_and_questions(transcript: str, language: str = "English") -> Tuple[str, str]:
    """Generates quiz questions and interview preparation questions based on the transcript."""
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    quiz_prompt = f"""
    Analyze the following transcript and generate a quiz.
    Target Language: {language}
    
    Generate:
    1. 5 Multiple Choice Questions (MCQs), each with 4 options and an indicated correct answer.
    2. 3 Short Answer Questions.
    3. 2 Long/Essay Questions.
    
    TRANSCRIPT:
    \"\"\"{transcript}\"\"\"
    
    Output ONLY a raw JSON object with this format (do not wrap in markdown ```json blocks):
    {{
        "mcqs": [
            {{
                "question": "Question text?",
                "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"],
                "answer": "A) opt1"
            }}
        ],
        "short_questions": [
            "Question 1?",
            "Question 2?"
        ],
        "long_questions": [
            "Question 1?",
            "Question 2?"
        ]
    }}
    """
    
    interview_prompt = f"""
    Analyze the following transcript and generate interview preparation questions.
    Target Language: {language}
    
    Generate:
    1. 3 Beginner-level interview questions.
    2. 3 Intermediate-level interview questions.
    3. 3 Advanced-level interview questions.
    
    TRANSCRIPT:
    \"\"\"{transcript}\"\"\"
    
    Output ONLY a raw JSON object with this format (do not wrap in markdown ```json blocks):
    {{
        "beginner": [
            "Question 1?", "Question 2?", "Question 3?"
        ],
        "intermediate": [
            "Question 1?", "Question 2?", "Question 3?"
        ],
        "advanced": [
            "Question 1?", "Question 2?", "Question 3?"
        ]
    }}
    """
    
    if provider == "groq":
        client = get_groq_client()
        if not client:
            empty_quiz = json.dumps({"mcqs": [], "short_questions": [], "long_questions": []})
            empty_interview = json.dumps({"beginner": [], "intermediate": [], "advanced": []})
            return empty_quiz, empty_interview
        
        # Quiz call
        try:
            logger.info("Requesting quiz from Groq...")
            chat_quiz = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful educational assessment assistant that always returns raw JSON."},
                    {"role": "user", "content": quiz_prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            quiz_json = chat_quiz.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating quiz from Groq: {e}")
            quiz_json = json.dumps({"error": str(e), "mcqs": [], "short_questions": [], "long_questions": []})
            
        # Interview call
        try:
            logger.info("Requesting interview questions from Groq...")
            chat_interview = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful career prep assistant that always returns raw JSON."},
                    {"role": "user", "content": interview_prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            interview_json = chat_interview.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating interview questions from Groq: {e}")
            interview_json = json.dumps({"error": str(e), "beginner": [], "intermediate": [], "advanced": []})
            
        return quiz_json, interview_json

    # Default: Gemini
    model = get_gemini_model()
    if not model:
        empty_quiz = json.dumps({"mcqs": [], "short_questions": [], "long_questions": []})
        empty_interview = json.dumps({"beginner": [], "intermediate": [], "advanced": []})
        return empty_quiz, empty_interview
        
    # Quiz call
    try:
        logger.info("Requesting quiz from Gemini...")
        res_quiz = model.generate_content(
            quiz_prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        quiz_json = res_quiz.text
    except Exception as e:
        logger.error(f"Error generating quiz from Gemini: {e}")
        quiz_json = json.dumps({"error": str(e), "mcqs": [], "short_questions": [], "long_questions": []})
        
    # Interview call
    try:
        logger.info("Requesting interview questions from Gemini...")
        res_interview = model.generate_content(
            interview_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        interview_json = res_interview.text
    except Exception as e:
        logger.error(f"Error generating interview questions from Gemini: {e}")
        interview_json = json.dumps({"error": str(e), "beginner": [], "intermediate": [], "advanced": []})
        
    return quiz_json, interview_json

def chat_with_transcript(transcript: str, question: str, chat_history: list = None) -> str:
    """Answers a question based on the transcript content using selected LLM provider (RAG approach)."""
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    context = f"""
    You are an AI learning assistant. Answer the user's question based strictly on the transcript below.
    If the answer cannot be found or inferred from the transcript, politely explain that the video does not cover that topic.
    
    TRANSCRIPT:
    \"\"\"{transcript}\"\"\"
    """
    
    if provider == "groq":
        client = get_groq_client()
        if not client:
            return "Groq API key is not set. Chat is unavailable."
            
        messages = []
        messages.append({"role": "system", "content": context})
        
        # Add history
        if chat_history:
            for msg in chat_history:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
                
        # Add active question
        messages.append({"role": "user", "content": question})
        
        try:
            logger.info("Requesting transcript chat completion from Groq...")
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile"
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in transcript chat from Groq: {e}")
            return f"Error communicating with Groq: {str(e)}"
            
    # Default: Gemini
    model = get_gemini_model()
    if not model:
        return "Gemini API key is not set. Chat is unavailable."
        
    messages = []
    # Feed system context
    messages.append({"role": "user", "parts": [context + "\n\nUnderstood? Please greet me and ask how you can help."]})
    # Simple reply from model to establish context
    messages.append({"role": "model", "parts": ["I have loaded the transcript context. How can I help you understand this video today?"]})
    
    # Add history
    if chat_history:
        for msg in chat_history:
            messages.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })
            
    # Add active question
    messages.append({"role": "user", "parts": [question]})
    
    try:
        logger.info("Requesting transcript chat completion from Gemini...")
        response = model.generate_content(messages)
        return response.text
    except Exception as e:
        logger.error(f"Error in transcript chat from Gemini: {e}")
        return f"Error communicating with Gemini: {str(e)}"
