@echo off
echo Starting AI Video Summarizer FastAPI Backend...
call .venv\Scripts\activate.bat
.venv\Scripts\python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
pause
