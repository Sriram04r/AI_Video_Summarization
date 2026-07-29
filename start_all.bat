@echo off
echo Starting AI Video Summarizer...

echo Starting Backend in a new window...
start "AI Video Summarizer - Backend" cmd /k "run_backend.bat"

echo Starting Frontend in a new window...
start "AI Video Summarizer - Frontend" cmd /k "run_frontend.bat"

echo Both services have been started! You can close this window.
pause
