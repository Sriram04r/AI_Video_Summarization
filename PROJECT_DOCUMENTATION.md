# 🧠 AI Video Summarization Platform - Official Documentation

## 📖 1. Project Overview
The **AI Video Summarization Platform** is a full-stack, cloud-native application designed to transform educational videos and long-form lectures into highly structured, actionable study materials. By leveraging state-of-the-art Generative AI (LLMs) and computer vision, the platform dramatically accelerates the learning process for students and professionals.

---

## 🏗️ 2. System Architecture

The application follows a decoupled client-server architecture, distributed across specialized cloud platforms to ensure scalability, security, and high availability.

### Architecture Diagram (Logical Flow)
1. **Client (Browser)** ➔ *Vercel Edge Network* (React UI)
2. **API Requests** ➔ *Render Web Service* (FastAPI Backend)
3. **Data Persistence** ➔ *Neon Serverless* (PostgreSQL Database)
4. **Third-Party Integrations**:
   - **Gemini / Groq**: Generative AI inference (Summaries, Quizzes, Chat)
   - **RapidAPI (Solid API)**: YouTube transcript proxy to bypass IP bans
   - **Google SMTP**: Secure email delivery for verification codes

---

## 💻 3. Technology Stack

### Frontend (Client-Side)
- **Framework**: React 18 (Bootstrapped with Vite for instant HMR and optimized builds)
- **Routing**: React Router v6
- **Styling**: Tailwind CSS (Utility-first CSS for rapid, responsive UI development)
- **Icons**: Lucide React
- **Markdown Parsing**: `react-markdown` (Renders AI-generated markdown safely)
- **Deployment**: Vercel

### Backend (Server-Side)
- **Framework**: FastAPI (High-performance Python web framework)
- **Server**: Uvicorn (ASGI web server implementation)
- **Authentication**: JWT (JSON Web Tokens) with `python-jose` and `passlib` (bcrypt hashing)
- **Database ORM**: SQLAlchemy (Synchronous session management)
- **Media Processing**: `opencv-python` (OpenCV for visual keyframe extraction)
- **Deployment**: Render

### Database & AI
- **Database**: PostgreSQL (Hosted on Neon.tech Serverless)
- **AI Inference Engine**: Google Gemini API / Groq API (LLaMA 3)
- **Audio Processing**: OpenAI Whisper (Local fallback for local video uploads)

---

## ✨ 4. Core Features & Workflows

### A. Authentication & Security
- **Registration**: Users create accounts. Passwords are mathematically hashed using Bcrypt before touching the database.
- **Login**: Issues a stateless JWT (JSON Web Token) valid for 24 hours. The token is sent in the `Authorization` header for all protected API routes.
- **Forgot Password**: 
  1. User enters email.
  2. Backend generates a 6-digit cryptographically random code.
  3. Code is emailed via Google SMTP.
  4. User verifies code and updates their password hash.

### B. Video Processing Engine
1. **Input Stage**: The user uploads an MP4 file or provides a YouTube URL.
2. **Extraction Stage**:
   - *YouTube*: Routes through RapidAPI to fetch the hidden subtitle transcript, bypassing YouTube's strict anti-bot datacenter firewalls.
   - *Local Video*: Extracts the audio track using `ffmpeg` and runs it through the Whisper Speech-to-Text model to generate a transcript. OpenCV concurrently scans the video frames, detecting significant pixel-shifts to save visual "Keyframes".
3. **AI Generation Stage**: The raw transcript is sent to the LLM with strict, heavily-engineered prompt templates to generate:
   - A short summary and bullet points
   - Detailed study notes
   - Practice quizzes
   - Mock interview questions
4. **Persistence Stage**: All generated markdown and metadata are committed to the Neon Postgres database.

### C. Interactive AI Lecture Companion
- Users can chat directly with an AI instructor on the Results page.
- **RAG (Retrieval-Augmented Generation)**: The AI is injected with the specific video's transcript as its "context window", allowing it to answer hyper-specific questions about the lecture without hallucinating.

---

## 🗄️ 5. Database Schema (Entity Relationship)

The PostgreSQL database consists of three primary tables connected via Foreign Keys:

**1. `users` Table**
- `user_id` (Primary Key, Integer)
- `username` (String)
- `email` (String, Unique)
- `hashed_password` (String)
- `reset_code` (String, Nullable)

**2. `videos` Table**
- `video_id` (Primary Key, Integer)
- `user_id` (Foreign Key ➔ `users.user_id`)
- `filename` (String)
- `file_path` (String) - *Stores S3/local path or `youtube://[id]`*
- `title` (String)
- `duration` (Float)
- `status` (String) - *'Pending', 'Processing', 'Success', 'Failed'*

**3. `summaries` Table**
- `summary_id` (Primary Key, Integer)
- `video_id` (Foreign Key ➔ `videos.video_id`)
- `transcript` (Text)
- `summary_text` (Text)
- `study_notes` (Text)
- `quiz` (Text)
- `interview_prep` (Text)
- `keyframes` (Text) - *JSON string array of image paths*

---

## 📡 6. REST API Endpoints Summary

### Auth (`/api/auth`)
- `POST /register`: Create a new user account.
- `POST /login`: Authenticate and receive JWT.
- `GET /me`: Get current logged-in user profile.
- `POST /forgot-password`: Send 6-digit OTP to email.
- `POST /verify-reset-code`: Validate the OTP.
- `POST /reset-password`: Set new hashed password.

### Video (`/api/video`)
- `POST /upload`: Upload local video and trigger processing.
- `POST /youtube`: Submit YouTube URL and trigger RapidAPI transcript extraction.
- `GET /status/{video_id}`: Long-polling endpoint for frontend loading screens.
- `GET /results/{video_id}`: Fetch the completed summaries and metadata.
- `POST /chat/{video_id}`: Converse with the AI regarding the specific video transcript.

### History (`/api/history`)
- `GET /videos`: Retrieve all videos processed by the logged-in user.
- `DELETE /clear`: Wipe the user's entire processing history.

---

## 🔒 7. Cloud Environment Variables Reference

To successfully run the backend, the following `.env` secrets must be populated on Render:

```env
# AI Models
GEMINI_API_KEY="AIzaSy..."
GROQ_API_KEY="gsk_..."

# Security
SECRET_KEY="random_secure_string"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="1440"

# Database (Neon)
DATABASE_URL="postgresql://neondb_owner:password@ep-restless.neon.tech/neondb?sslmode=require"

# Email Verification (Google)
SMTP_EMAIL="your_email@gmail.com"
SMTP_PASSWORD="16_letter_app_password"

# Proxies
RAPID_API_KEY="rapid_api_secret_key"
RAPID_API_HOST="youtube-transcript3.p.rapidapi.com"
```
