# 🧠 AI Video Summarization & Study Notes Generator

A full-stack, cloud-native AI application that transforms any educational video or lecture into comprehensive study materials. Built with React, FastAPI, and powered by Gemini/Groq's lightning-fast AI inference.

## ✨ Features

- **Upload Local & YouTube Videos**: Process educational MP4 videos directly from your device, or paste a YouTube link to instantly summarize it.
- **Smart Summarization**: Automatically generates structured summaries, bullet points, and key takeaways.
- **Study Notes & Quizzes**: Automatically creates detailed study notes, practice quizzes, and interview prep questions based on the video content.
- **Interactive AI Chat**: Ask questions directly to an AI instructor about the video content.
- **Visual Keyframes**: Uses OpenCV to detect scene changes and extract important presentation slides or visual keyframes from uploaded videos.
- **PDF Export**: Download your AI-generated study materials as a clean, formatted PDF report.
- **Authentication**: Full user authentication system including secure signup, login, and a "Forgot Password" flow with email verification codes.
- **Permanent History**: All your video summaries and history are securely saved in a cloud database.

## 🚀 Cloud-Native Architecture

This application is designed for production and deployed across multiple specialized cloud services:

1. **Frontend (Vercel)**: A responsive, glassmorphic React UI built with TailwindCSS.
2. **Backend (Render)**: A robust Python FastAPI server that handles audio extraction, AI processing, and API routing.
3. **Database (Neon Postgres)**: A serverless PostgreSQL database that permanently stores user accounts, video metadata, and generated summaries.
4. **Email (Google SMTP)**: Securely sends out 6-digit verification codes for password resets.
5. **Proxy (RapidAPI)**: Silently bypasses YouTube's strict datacenter IP bans to reliably fetch video transcripts from the cloud.

## 💻 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/Sriram04r/AI_Video_Summarization.git
cd AI_Video_Summarization
```

### 2. Setup the Environment Variables
Create a `.env` file in the root directory and add the following keys:
```env
# AI APIs
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Database
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# Authentication Secrets
SECRET_KEY=your_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email Setup for Forgot Password
SMTP_EMAIL=your_gmail_address
SMTP_PASSWORD=your_16_letter_google_app_password

# YouTube Transcript Proxy
RAPID_API_KEY=your_rapidapi_key
RAPID_API_HOST=youtube-transcript3.p.rapidapi.com
```

### 3. Setup the Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Setup the Frontend
```bash
cd frontend
npm install
npm run dev
```

## ☁️ Deployment Guide

To deploy this application to the cloud, follow these steps:

### 1. Database (Neon Postgres)
1. Go to [Neon.tech](https://neon.tech) and create a free project.
2. Copy your Connection String (`DATABASE_URL`).

### 2. Backend (Render)
1. Go to [Render.com](https://render.com) and create a new **Web Service**.
2. Connect your GitHub repository.
3. Set the Build Command to: `pip install -r requirements.txt`
4. Set the Start Command to: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. In the **Environment Variables** section, paste ALL the variables from your `.env` file (including your Neon `DATABASE_URL`).

### 3. YouTube Proxy (RapidAPI)
1. Go to [RapidAPI](https://rapidapi.com) and search for the **YouTube Transcript3** API by Solid API.
2. Click **Subscribe to Test** (Free Tier).
3. Copy your API Key and add it to your Render Environment Variables as `RAPID_API_KEY`.

### 4. Frontend (Vercel)
1. Go to [Vercel.com](https://vercel.com) and create a new project.
2. Connect your GitHub repository.
3. Change the **Root Directory** to `frontend`.
4. In Environment Variables, add:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://your-render-backend-url.onrender.com`
5. Click **Deploy**.

Your application is now live on the internet, secure, and ready to scale!